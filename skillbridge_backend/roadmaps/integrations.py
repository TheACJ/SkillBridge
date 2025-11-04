import os
import openai
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenAIIntegration:
    """Integration with OpenAI for roadmap generation"""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))

    def generate_roadmap(self, domain: str, skill_level: str = 'beginner',
                        time_availability: str = 'part-time',
                        user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a personalized learning roadmap using OpenAI
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured, using mock response")
            return self._generate_mock_roadmap(domain, skill_level, time_availability)

        try:
            prompt = self._build_roadmap_prompt(domain, skill_level, time_availability, user_context)

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert learning path designer. Create detailed, actionable learning roadmaps for developers. Focus on practical skills, real projects, and measurable progress."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )

            roadmap_text = response.choices[0].message.content.strip()
            return self._parse_roadmap_response(roadmap_text, domain)

        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._generate_mock_roadmap(domain, skill_level, time_availability)
        except Exception as e:
            logger.error(f"Error generating roadmap: {str(e)}")
            return self._generate_mock_roadmap(domain, skill_level, time_availability)

    def _build_roadmap_prompt(self, domain: str, skill_level: str,
                             time_availability: str, user_context: Optional[Dict[str, Any]]) -> str:
        """Build the prompt for OpenAI"""

        time_descriptions = {
            'part-time': '5-10 hours per week',
            'full-time': '20-30 hours per week',
            'intensive': '40+ hours per week'
        }

        prompt = f"""
Create a detailed learning roadmap for {domain} at {skill_level} level.
Time availability: {time_descriptions.get(time_availability, time_availability)}

Requirements:
1. 4-6 modules with clear learning objectives
2. Each module should have 2-4 practical resources (courses, tutorials, projects)
3. Include estimated time for each module
4. Focus on hands-on learning and real projects
5. Consider progressive difficulty building
6. Include assessment methods or projects

Format as JSON with this structure:
{{
    "domain": "{domain}",
    "modules": [
        {{
            "name": "Module Name",
            "resources": [
                {{
                    "title": "Resource Title",
                    "platform": "Platform Name",
                    "url": "https://example.com",
                    "difficulty": "Beginner|Intermediate|Advanced",
                    "duration": "X hours"
                }}
            ],
            "estimated_time": 10,
            "completed": false
        }}
    ],
    "progress": 0,
    "estimated_completion_weeks": 8
}}
"""

        if user_context:
            prompt += f"\n\nUser Context: {user_context}"

        return prompt

    def _parse_roadmap_response(self, response_text: str, domain: str) -> Dict[str, Any]:
        """Parse the OpenAI response into structured roadmap data"""
        try:
            # Try to extract JSON from the response
            import json
            import re

            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                roadmap_data = json.loads(json_match.group())
                return roadmap_data

            # If no JSON found, create structured response from text
            return self._generate_mock_roadmap(domain, 'beginner', 'part-time')

        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse OpenAI response: {str(e)}")
            return self._generate_mock_roadmap(domain, 'beginner', 'part-time')

    def _generate_mock_roadmap(self, domain: str, skill_level: str, time_availability: str) -> Dict[str, Any]:
        """Generate a mock roadmap when OpenAI is unavailable"""
        logger.info(f"Generating mock roadmap for {domain} ({skill_level})")

        base_resources = {
            'python': [
                {
                    'title': 'Python for Everybody',
                    'platform': 'Coursera',
                    'url': 'https://www.coursera.org/specializations/python',
                    'difficulty': 'Beginner',
                    'duration': '8 weeks'
                },
                {
                    'title': 'Automate the Boring Stuff with Python',
                    'platform': 'Free',
                    'url': 'https://automatetheboringstuff.com',
                    'difficulty': 'Beginner',
                    'duration': 'Self-paced'
                }
            ],
            'web-development': [
                {
                    'title': 'HTML & CSS Full Course',
                    'platform': 'freeCodeCamp',
                    'url': 'https://www.freecodecamp.org/learn/responsive-web-design/',
                    'difficulty': 'Beginner',
                    'duration': '300 hours'
                }
            ]
        }

        domain_key = domain.lower().replace(' ', '-')
        resources = base_resources.get(domain_key, base_resources['python'])

        modules = [
            {
                'name': f'Introduction to {domain}',
                'resources': resources[:2],
                'estimated_time': 20,
                'completed': False
            },
            {
                'name': f'Core {domain} Concepts',
                'resources': resources,
                'estimated_time': 30,
                'completed': False
            },
            {
                'name': f'Building {domain} Projects',
                'resources': [
                    {
                        'title': f'Build a {domain} Portfolio Project',
                        'platform': 'GitHub',
                        'url': 'https://github.com',
                        'difficulty': skill_level.title(),
                        'duration': 'Variable'
                    }
                ],
                'estimated_time': 40,
                'completed': False
            }
        ]

        return {
            'domain': domain,
            'modules': modules,
            'progress': 0,
            'estimated_completion_weeks': 6
        }

    def validate_api_key(self) -> bool:
        """Validate that the OpenAI API key is working"""
        if not self.api_key:
            return False

        try:
            # Make a simple test request
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI API key validation failed: {str(e)}")
            return False