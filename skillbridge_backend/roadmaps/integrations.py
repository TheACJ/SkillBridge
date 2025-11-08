import os
import json
import time
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 60, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def allow_call(self) -> bool:
        """Check if a call is allowed within rate limits"""
        now = time.time()
        
        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        # Check if we can make another call
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def time_until_next_call(self) -> float:
        """Get time until next allowed call"""
        if not self.calls:
            return 0.0
        
        oldest_call = min(self.calls)
        return max(0, self.time_window - (time.time() - oldest_call))


class CostTracker:
    """Track API costs and usage"""
    
    def __init__(self, daily_limit: float = None):
        self.daily_limit = daily_limit or getattr(settings, 'OPENAI_DAILY_COST_LIMIT', 50.0)  # $50 per day default
        self.current_cost = 0.0
        self.request_count = 0
        self.last_reset = datetime.now().date()
    
    def can_make_request(self, estimated_cost: float = 0.1) -> bool:
        """Check if request can be made within cost limits"""
        self._reset_if_new_day()
        return (self.current_cost + estimated_cost) <= self.daily_limit
    
    def record_request(self, cost: float):
        """Record API request cost"""
        self._reset_if_new_day()
        self.current_cost += cost
        self.request_count += 1
    
    def _reset_if_new_day(self):
        """Reset counters if new day"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.current_cost = 0.0
            self.request_count = 0
            self.last_reset = today
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        self._reset_if_new_day()
        return {
            'current_cost': round(self.current_cost, 4),
            'daily_limit': self.daily_limit,
            'remaining_budget': round(self.daily_limit - self.current_cost, 4),
            'request_count': self.request_count,
            'cost_percentage': round((self.current_cost / self.daily_limit) * 100, 2)
        }


class CircuitBreaker:
    """Circuit breaker pattern for API resilience"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        if self.state == 'CLOSED':
            return True
        elif self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful execution"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'


class OpenAIIntegration:
    """Enhanced OpenAI integration with caching, retry logic, cost monitoring, and rate limiting"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.client = None
        self.rate_limiter = RateLimiter(max_calls=60, time_window=60)  # 60 calls per minute
        self.cost_tracker = CostTracker()
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        self.cache_ttl = getattr(settings, 'ROADMAP_CACHE_TTL', 3600)  # 1 hour default
        
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                # Test the connection
                if self._validate_api_key():
                    logger.info("OpenAI integration initialized successfully")
                else:
                    logger.warning("OpenAI API key validation failed")
                    self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        else:
            logger.warning("OpenAI API key not configured, using mock responses")
    
    def generate_roadmap(self, domain: str, skill_level: str, time_availability: str, 
                        user_context: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate a personalized roadmap using OpenAI with advanced features
        
        Args:
            domain: Learning domain (e.g., 'Python', 'JavaScript')
            skill_level: 'beginner', 'intermediate', or 'advanced'
            time_availability: 'part-time', 'full-time', or 'casual'
            user_context: User profile information for personalization
            use_cache: Whether to use caching for this request
            
        Returns:
            Dict containing roadmap data
        """
        # Generate cache key
        cache_key = self._generate_cache_key(domain, skill_level, time_availability, user_context)
        
        # Check cache first
        if use_cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached roadmap for {domain} ({skill_level})")
                return cached_result
        
        # Check rate limits and cost limits
        if not self.rate_limiter.allow_call():
            wait_time = self.rate_limiter.time_until_next_call()
            logger.warning(f"Rate limit exceeded, waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        
        if not self.cost_tracker.can_make_request():
            logger.warning("Daily cost limit exceeded, using fallback")
            return self._generate_enhanced_mock_roadmap(domain, skill_level, time_availability)
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit breaker is OPEN, using fallback")
            return self._generate_enhanced_mock_roadmap(domain, skill_level, time_availability)
        
        if not self.client:
            logger.warning("OpenAI client not available, using enhanced mock")
            return self._generate_enhanced_mock_roadmap(domain, skill_level, time_availability)
        
        # Retry logic with exponential backoff
        max_retries = getattr(settings, 'OPENAI_MAX_RETRIES', 3)
        base_delay = getattr(settings, 'OPENAI_RETRY_DELAY', 1.0)
        
        for attempt in range(max_retries + 1):
            try:
                # Prepare the enhanced prompt
                prompt = self._build_enhanced_prompt(domain, skill_level, time_availability, user_context)
                
                # Make API call
                start_time = time.time()
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=3000,
                    temperature=0.7,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.1
                )
                
                # Record success
                self.circuit_breaker.record_success()
                
                # Parse and validate response
                roadmap_data = self._parse_and_validate_response(
                    response.choices[0].message.content, 
                    domain, 
                    skill_level,
                    time_availability
                )
                
                if roadmap_data:
                    # Calculate and record cost
                    estimated_cost = self._estimate_cost(response.usage.total_tokens if response.usage else 1000)
                    self.cost_tracker.record_request(estimated_cost)
                    
                    # Add metadata
                    roadmap_data.update({
                        'domain': domain,
                        'skill_level': skill_level,
                        'time_availability': time_availability,
                        'generated_by': 'openai',
                        'generated_at': datetime.now().isoformat(),
                        'cost': estimated_cost,
                        'response_time': round(time.time() - start_time, 2)
                    })
                    
                    # Cache the result
                    if use_cache:
                        cache.set(cache_key, roadmap_data, self.cache_ttl)
                    
                    logger.info(f"Generated roadmap for {domain} ({skill_level}) using OpenAI")
                    return roadmap_data
                else:
                    raise Exception("Failed to parse response")
                    
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    logger.error("Max retries exceeded due to rate limits")
                    self.circuit_breaker.record_failure()
                    return self._generate_enhanced_mock_roadmap(domain, skill_level, time_availability)
                    
            except openai.APITimeoutError as e:
                logger.warning(f"Timeout error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    logger.error("Max retries exceeded due to timeouts")
                    self.circuit_breaker.record_failure()
                    return self._generate_enhanced_mock_roadmap(domain, skill_level, time_availability)
                    
            except openai.APIError as e:
                logger.error(f"API error (attempt {attempt + 1}): {str(e)}")
                self.circuit_breaker.record_failure()
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    return self._generate_enhanced_mock_roadmap(domain, skill_level, time_availability)
                    
            except Exception as e:
                logger.error(f"Unexpected error (attempt {attempt + 1}): {str(e)}")
                self.circuit_breaker.record_failure()
                if attempt == max_retries:
                    return self._generate_enhanced_mock_roadmap(domain, skill_level, time_availability)
                else:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
    
    def _generate_cache_key(self, domain: str, skill_level: str, time_availability: str,
                           user_context: Dict[str, Any]) -> str:
        """Generate a cache key for the request"""
        # Create a hash based on the request parameters
        if user_context is None:
            user_context = {}

        cache_data = {
            'domain': domain.lower().strip(),
            'skill_level': skill_level.lower().strip(),
            'time_availability': time_availability.lower().strip(),
            'user_skills': sorted(user_context.get('skills', [])),
            'learning_goals': sorted(user_context.get('learning_goals', [])),
            'location': user_context.get('location', '').lower().strip()
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"roadmap_{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI"""
        return """You are an expert learning path generator and educational consultant. 
        
Your task is to create comprehensive, personalized learning roadmaps that are:
- Practical and hands-on oriented
- Progressive and well-structured
- Tailored to the learner's background and goals
- Include specific resources and time estimates
- Focus on real-world applications and projects

Each roadmap should be detailed enough to serve as a complete learning guide while being flexible enough to accommodate different learning speeds and styles."""
    
    def _build_enhanced_prompt(self, domain: str, skill_level: str, time_availability: str, 
                              user_context: Dict[str, Any]) -> str:
        """Build an enhanced prompt for better AI responses"""
        skills = user_context.get('skills', [])
        learning_goals = user_context.get('learning_goals', [])
        location = user_context.get('location', 'Not specified')
        availability_hours = user_context.get('availability', 'Not specified')
        experience_years = user_context.get('experience_years', 0)
        
        # Customize prompt based on skill level
        level_specific_instructions = {
            'beginner': "Focus on fundamentals and ensure no prior knowledge is assumed. Include extra foundational concepts.",
            'intermediate': "Build on existing knowledge and introduce more complex concepts. Include practical applications.",
            'advanced': "Focus on expert-level topics, best practices, and cutting-edge developments. Include complex projects."
        }
        
        # Time-based adjustments
        time_adjustments = {
            'part-time': "Optimize for 5-10 hours per week with flexible scheduling.",
            'full-time': "Optimize for 20-40 hours per week with intensive learning pace.",
            'casual': "Optimize for 2-5 hours per week with relaxed progression."
        }
        
        prompt = f"""
        Create a comprehensive, personalized learning roadmap for {domain} with these specifications:
        
        **Learner Profile:**
        - Skill Level: {skill_level}
        - Current Skills: {', '.join(skills) if skills else 'No prior experience specified'}
        - Learning Goals: {', '.join(learning_goals) if learning_goals else 'General proficiency in the domain'}
        - Experience: {experience_years} years
        - Location: {location}
        - Available Time: {availability_hours} hours per week
        - Learning Style Preference: {time_availability}
        
        **Domain:** {domain}
        **Target Level:** {skill_level.upper()}
        **Learning Pace:** {time_availability}
        
        **Specific Instructions:**
        {level_specific_instructions.get(skill_level, "Create a balanced learning path.")}
        {time_adjustments.get(time_availability, "Adapt the pace accordingly.")}
        
        **Roadmap Requirements:**
        1. Create 6-8 learning modules that progress logically
        2. Each module should have:
           - Clear learning objectives (3-5 specific goals)
           - Estimated completion time (in hours)
           - 3-5 high-quality resources with specific URLs
           - Practical exercises or projects
           - Self-assessment criteria
        3. Include milestone checkpoints every 2-3 modules
        4. Add prerequisite information for each module
        5. Suggest complementary skills to learn alongside
        6. Include career progression suggestions
        7. Add real-world project ideas
        
        **Resource Guidelines:**
        - Include a mix of free and paid resources
        - Prioritize interactive and hands-on content
        - Include official documentation and community resources
        - Add video tutorials, written guides, and practice platforms
        - Ensure resources are current and up-to-date
        
        **Output Format:**
        Please respond with a JSON object in this exact format:
        {{
            "domain": "{domain}",
            "skill_level": "{skill_level}",
            "estimated_duration_weeks": 12,
            "total_estimated_hours": 120,
            "milestones": [
                {{"week": 4, "achievement": "Foundation Complete"}},
                {{"week": 8, "achievement": "Intermediate Skills"}},
                {{"week": 12, "achievement": "Ready for Advanced Projects"}}
            ],
            "modules": [
                {{
                    "id": 1,
                    "title": "Module Title",
                    "description": "What will be learned and why it's important",
                    "objectives": [
                        "Specific learning objective 1",
                        "Specific learning objective 2",
                        "Specific learning objective 3"
                    ],
                    "estimated_hours": 15,
                    "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
                    "resources": [
                        {{
                            "title": "Resource Title",
                            "type": "tutorial|video|documentation|practice|project",
                            "platform": "Platform Name",
                            "url": "https://example.com",
                            "free": true,
                            "estimated_time": "2 hours"
                        }}
                    ],
                    "exercises": [
                        {{
                            "title": "Exercise Title",
                            "description": "What to practice",
                            "estimated_time": "1 hour"
                        }}
                    ],
                    "project": {{
                        "title": "Project Title",
                        "description": "Real-world project to build",
                        "complexity": "beginner|intermediate|advanced"
                    }},
                    "assessment": "How to measure completion and understanding"
                }}
            ]
        }}
        
        Ensure the roadmap is:
        - Practical and immediately actionable
        - Progressive and builds upon previous knowledge
        - Tailored to the specific skill level and time constraints
        - Includes diverse learning resources and formats
        - Leads to demonstrable skills and portfolio projects
        """
        
        return prompt
    
    def _parse_and_validate_response(self, response_text: str, domain: str, 
                                   skill_level: str, time_availability: str) -> Optional[Dict[str, Any]]:
        """Parse and validate OpenAI response with enhanced error handling"""
        try:
            # Try to extract JSON from the response
            import re
            
            # Look for JSON objects in the response
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            for json_str in json_matches:
                try:
                    roadmap_data = json.loads(json_str)
                    
                    # Validate required fields
                    if self._validate_roadmap_structure(roadmap_data):
                        # Add missing required fields for compatibility
                        modules = roadmap_data.get('modules', [])
                        for i, module in enumerate(modules):
                            # Ensure required module fields
                            module.setdefault('name', module.get('title', f'Module {i+1}'))
                            module.setdefault('completed', False)
                            
                            # Ensure resources have required structure
                            resources = module.get('resources', [])
                            for resource in resources:
                                if isinstance(resource, dict):
                                    resource.setdefault('title', 'Resource')
                                    resource.setdefault('platform', 'Web')
                                    resource.setdefault('url', 'https://example.com')
                        
                        # Calculate progress (starts at 0)
                        roadmap_data.setdefault('progress', 0.0)
                        roadmap_data['modules'] = modules
                        
                        return roadmap_data
                        
                except json.JSONDecodeError:
                    continue
            
            # If no valid JSON found, create structured response
            logger.warning("No valid JSON found in response, creating fallback structure")
            return self._create_fallback_structure(response_text, domain, skill_level, time_availability)
            
        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}")
            return None
    
    def _validate_roadmap_structure(self, data: Dict[str, Any]) -> bool:
        """Validate that the roadmap has the required structure"""
        required_fields = ['domain', 'modules']
        has_required = all(field in data for field in required_fields)
        
        if not has_required:
            return False
        
        # Validate modules
        modules = data.get('modules', [])
        if not isinstance(modules, list) or len(modules) == 0:
            return False
        
        # Check that each module has basic structure
        for module in modules:
            if not isinstance(module, dict):
                return False
            if not any(field in module for field in ['title', 'name']):
                return False
        
        return True
    
    def _create_fallback_structure(self, response_text: str, domain: str, 
                                 skill_level: str, time_availability: str) -> Dict[str, Any]:
        """Create a structured response from unstructured text"""
        # Extract key phrases and topics from the response
        import re
        
        # Find numbered lists or bullet points
        sections = re.findall(r'\d+\.\s*([^0-9\n]+)', response_text)
        if not sections:
            sections = re.findall(r'[-•]\s*([^\n]+)', response_text)
        
        modules = []
        for i, section in enumerate(sections[:7]):  # Limit to 7 modules
            section = section.strip()
            if len(section) > 10:  # Ignore very short sections
                modules.append({
                    'name': f'Module {i+1}: {section[:50]}...',
                    'description': f'Learn about {section[:100]}...',
                    'objectives': [
                        f'Understand {section[:30]} concepts',
                        f'Apply {section[:30]} in practice',
                        f'Master {section[:30]} fundamentals'
                    ],
                    'estimated_time': 15 + (i * 5),  # Incremental time estimates
                    'resources': [
                        {
                            'title': f'{section[:30]} Tutorial',
                            'platform': 'Web',
                            'url': 'https://example.com'
                        }
                    ],
                    'completed': False
                })
        
        # If no sections found, create basic structure
        if not modules:
            modules = self._get_default_modules(domain, skill_level)
        
        return {
            'domain': domain,
            'skill_level': skill_level,
            'time_availability': time_availability,
            'estimated_duration_weeks': 12,
            'progress': 0.0,
            'modules': modules,
            'generated_by': 'openai_fallback'
        }
    
    def _get_default_modules(self, domain: str, skill_level: str) -> List[Dict[str, Any]]:
        """Get default module structure for fallback"""
        base_modules = [
            f'{domain} Fundamentals',
            f'{domain} Core Concepts',
            f'{domain} Practical Applications',
            f'{domain} Advanced Topics',
            f'{domain} Project Development',
            f'{domain} Best Practices'
        ]
        
        return [
            {
                'name': module,
                'description': f'Comprehensive study of {module.lower()}',
                'objectives': [
                    f'Understand {module} concepts',
                    f'Apply {module} in practical scenarios',
                    f'Master {module} implementation'
                ],
                'estimated_time': 20,
                'resources': [
                    {
                        'title': f'{module} Guide',
                        'platform': 'Web',
                        'url': 'https://example.com'
                    }
                ],
                'completed': False
            }
            for module in base_modules
        ]
    
    def _generate_enhanced_mock_roadmap(self, domain: str, skill_level: str, 
                                      time_availability: str) -> Dict[str, Any]:
        """Generate an enhanced mock roadmap with better structure"""
        logger.info(f"Generating enhanced mock roadmap for {domain} ({skill_level})")
        
        # Enhanced domain-specific modules
        domain_modules = {
            'python': [
                {'title': 'Python Programming Fundamentals', 'hours': 25, 'difficulty': 'beginner'},
                {'title': 'Data Structures and Algorithms', 'hours': 30, 'difficulty': 'intermediate'},
                {'title': 'Object-Oriented Programming', 'hours': 20, 'difficulty': 'intermediate'},
                {'title': 'Web Development with Django/Flask', 'hours': 35, 'difficulty': 'intermediate'},
                {'title': 'Data Science and Machine Learning', 'hours': 40, 'difficulty': 'advanced'},
                {'title': 'Testing and Debugging', 'hours': 15, 'difficulty': 'intermediate'},
                {'title': 'Deployment and DevOps', 'hours': 20, 'difficulty': 'advanced'}
            ],
            'javascript': [
                {'title': 'JavaScript Fundamentals', 'hours': 20, 'difficulty': 'beginner'},
                {'title': 'DOM Manipulation and Events', 'hours': 15, 'difficulty': 'beginner'},
                {'title': 'Asynchronous JavaScript', 'hours': 25, 'difficulty': 'intermediate'},
                {'title': 'Modern JavaScript (ES6+)', 'hours': 20, 'difficulty': 'intermediate'},
                {'title': 'Frontend Framework (React/Vue)', 'hours': 30, 'difficulty': 'intermediate'},
                {'title': 'Node.js and Backend Development', 'hours': 25, 'difficulty': 'advanced'},
                {'title': 'Testing and Deployment', 'hours': 15, 'difficulty': 'intermediate'}
            ],
            'web_development': [
                {'title': 'HTML & CSS Fundamentals', 'hours': 20, 'difficulty': 'beginner'},
                {'title': 'Responsive Design and Flexbox/Grid', 'hours': 15, 'difficulty': 'beginner'},
                {'title': 'JavaScript Basics', 'hours': 25, 'difficulty': 'beginner'},
                {'title': 'Frontend Framework', 'hours': 30, 'difficulty': 'intermediate'},
                {'title': 'Backend API Development', 'hours': 25, 'difficulty': 'intermediate'},
                {'title': 'Database Design and Management', 'hours': 20, 'difficulty': 'intermediate'},
                {'title': 'Deployment and DevOps', 'hours': 15, 'difficulty': 'advanced'}
            ]
        }
        
        # Get modules for domain or create custom ones
        modules_data = domain_modules.get(domain.lower().replace(' ', '_'), [
            {'title': f'{domain} Fundamentals', 'hours': 20, 'difficulty': 'beginner'},
            {'title': f'{domain} Core Concepts', 'hours': 25, 'difficulty': 'intermediate'},
            {'title': f'{domain} Advanced Applications', 'hours': 30, 'difficulty': 'advanced'},
            {'title': f'{domain} Professional Projects', 'hours': 25, 'difficulty': 'advanced'},
            {'title': f'{domain} Best Practices', 'hours': 15, 'difficulty': 'intermediate'}
        ])
        
        # Filter by skill level
        if skill_level == 'beginner':
            modules_data = [m for m in modules_data if m['difficulty'] in ['beginner', 'intermediate']]
        elif skill_level == 'intermediate':
            modules_data = [m for m in modules_data if m['difficulty'] in ['intermediate']]
        else:  # advanced
            modules_data = [m for m in modules_data if m['difficulty'] in ['intermediate', 'advanced']]
        
        # Calculate duration based on time availability
        if time_availability == 'part-time':
            weeks_per_hour = 0.2  # 5 hours per week
        elif time_availability == 'full-time':
            weeks_per_hour = 0.05  # 20 hours per week
        else:  # casual
            weeks_per_hour = 0.3  # 3 hours per week
        
        total_hours = sum(module['hours'] for module in modules_data)
        estimated_weeks = max(4, int(total_hours * weeks_per_hour))
        
        # Create enhanced roadmap structure
        roadmap = {
            'domain': domain,
            'skill_level': skill_level,
            'time_availability': time_availability,
            'estimated_duration_weeks': estimated_weeks,
            'total_estimated_hours': total_hours,
            'progress': 0.0,
            'modules': [],
            'milestones': self._generate_milestones(estimated_weeks),
            'generated_by': 'enhanced_mock_generator',
            'generated_at': datetime.now().isoformat(),
            'cost': 0.0,  # Mock generation is free
            'response_time': 0.0
        }
        
        # Generate enhanced module details
        for i, module_data in enumerate(modules_data):
            module = {
                'id': i + 1,
                'name': module_data['title'],
                'description': f'Comprehensive study of {module_data["title"]} with hands-on projects and real-world applications',
                'objectives': [
                    f'Master {module_data["title"]} fundamentals and core concepts',
                    f'Apply {module_data["title"]} in practical, real-world scenarios',
                    f'Develop expertise in {module_data["title"]} best practices',
                    f'Build portfolio projects demonstrating {module_data["title"]} proficiency',
                    f'Prepare for professional {module_data["title"]} development'
                ],
                'estimated_hours': module_data['hours'],
                'difficulty': module_data['difficulty'],
                'completed': False,
                'resources': self._generate_resources(module_data['title'], domain),
                'exercises': self._generate_exercises(module_data['title']),
                'project': {
                    'title': f'{module_data["title"]} Capstone Project',
                    'description': f'Build a comprehensive {module_data["title"]} application showcasing all learned concepts',
                    'complexity': module_data['difficulty']
                },
                'assessment': f'Demonstrate proficiency through practical implementation and code review'
            }
            roadmap['modules'].append(module)
        
        return roadmap
    
    def _generate_milestones(self, total_weeks: int) -> List[Dict[str, Any]]:
        """Generate learning milestones"""
        milestones = []
        checkpoint_weeks = [int(total_weeks * 0.25), int(total_weeks * 0.5), int(total_weeks * 0.75), total_weeks]
        milestone_names = ['Foundation Complete', 'Core Skills Mastered', 'Advanced Proficiency', 'Learning Goal Achieved']
        
        for i, week in enumerate(checkpoint_weeks):
            milestones.append({
                'week': week,
                'achievement': milestone_names[i],
                'description': f'Reach this milestone to validate your progress in {milestone_names[i].lower()}'
            })
        
        return milestones
    
    def _generate_resources(self, module_title: str, domain: str) -> List[Dict[str, Any]]:
        """Generate comprehensive resources for a module"""
        resources = [
            {
                'title': f'{module_title} - Official Documentation',
                'type': 'documentation',
                'platform': 'Official Docs',
                'url': f'https://docs.example.com/{domain.lower().replace(" ", "-")}',
                'free': True,
                'estimated_time': '2-3 hours'
            },
            {
                'title': f'{module_title} - Interactive Tutorial',
                'type': 'tutorial',
                'platform': 'Interactive Learning',
                'url': 'https://example.com/interactive-tutorial',
                'free': True,
                'estimated_time': '4-5 hours'
            },
            {
                'title': f'{module_title} - Video Course',
                'type': 'video',
                'platform': 'Educational Platform',
                'url': 'https://youtube.com/watch?v=example',
                'free': True,
                'estimated_time': '6-8 hours'
            },
            {
                'title': f'{module_title} - Hands-on Project',
                'type': 'project',
                'platform': 'Practice Platform',
                'url': 'https://example.com/project',
                'free': True,
                'estimated_time': '8-10 hours'
            }
        ]
        
        return resources
    
    def _generate_exercises(self, module_title: str) -> List[Dict[str, Any]]:
        """Generate practice exercises for a module"""
        exercises = [
            {
                'title': f'Basic {module_title} Exercise',
                'description': f'Practice fundamental {module_title} concepts with guided examples',
                'estimated_time': '1-2 hours'
            },
            {
                'title': f'Intermediate {module_title} Challenge',
                'description': f'Solve more complex {module_title} problems independently',
                'estimated_time': '2-3 hours'
            },
            {
                'title': f'Advanced {module_title} Project',
                'description': f'Apply {module_title} knowledge in a comprehensive project',
                'estimated_time': '4-6 hours'
            }
        ]
        
        return exercises
    
    def _estimate_cost(self, tokens_used: int) -> float:
        """Estimate cost based on tokens used (GPT-3.5-turbo pricing)"""
        # GPT-3.5-turbo pricing: $0.0015 per 1K tokens for input, $0.002 per 1K for output
        # Assume 75% input, 25% output for simplification
        input_tokens = int(tokens_used * 0.75)
        output_tokens = int(tokens_used * 0.25)
        
        input_cost = (input_tokens / 1000) * 0.0015
        output_cost = (output_tokens / 1000) * 0.002
        
        return round(input_cost + output_cost, 6)
    
    def _validate_api_key(self) -> bool:
        """Validate the OpenAI API key with a minimal request"""
        if not self.client:
            return False
        
        try:
            # Make a small test request
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI API key validation failed: {str(e)}")
            return False
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get comprehensive integration statistics"""
        return {
            'client_available': self.client is not None,
            'rate_limiter': {
                'max_calls_per_minute': self.rate_limiter.max_calls,
                'current_calls': len(self.rate_limiter.calls)
            },
            'cost_tracking': self.cost_tracker.get_usage_stats(),
            'circuit_breaker': {
                'state': self.circuit_breaker.state,
                'failure_count': self.circuit_breaker.failure_count,
                'failure_threshold': self.circuit_breaker.failure_threshold
            },
            'cache_ttl': self.cache_ttl
        }
    
    def clear_cache(self, domain: str = None, skill_level: str = None):
        """Clear roadmap cache, optionally filtered by domain/skill level"""
        # Use Django's cache clear method for all roadmap cache
        # For pattern-based deletion, we'd need Redis or Memcached
        cache.clear()
        logger.info("Cache cleared successfully")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Check API key
        api_key_ok = self._validate_api_key()
        health_status['checks']['api_key'] = {
            'status': 'healthy' if api_key_ok else 'unhealthy',
            'message': 'API key valid' if api_key_ok else 'API key invalid or expired'
        }
        
        # Check rate limiter
        health_status['checks']['rate_limiter'] = {
            'status': 'healthy',
            'message': f'{len(self.rate_limiter.calls)} calls in current window'
        }
        
        # Check cost limits
        cost_stats = self.cost_tracker.get_usage_stats()
        health_status['checks']['cost_tracking'] = {
            'status': 'healthy' if cost_stats['cost_percentage'] < 90 else 'warning',
            'message': f'{cost_stats["cost_percentage"]:.1f}% of daily limit used'
        }
        
        # Check circuit breaker
        health_status['checks']['circuit_breaker'] = {
            'status': 'healthy' if self.circuit_breaker.state != 'OPEN' else 'unhealthy',
            'message': f'Circuit breaker is {self.circuit_breaker.state}'
        }
        
        # Determine overall health
        if any(check['status'] == 'unhealthy' for check in health_status['checks'].values()):
            health_status['overall_status'] = 'unhealthy'
        elif any(check['status'] == 'warning' for check in health_status['checks'].values()):
            health_status['overall_status'] = 'degraded'
        
        return health_status