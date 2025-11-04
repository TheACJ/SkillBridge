use crate::models::{User, Mentor, MatchResult, CompatibilityFactors};
use petgraph::graph::{Graph, NodeIndex};
use petgraph::algo::matching;
use rayon::prelude::*;
use std::collections::HashMap;
use std::time::{Instant, Duration};

pub struct MentorMatcher {
    algorithm_version: String,
}

impl MentorMatcher {
    pub fn new() -> Self {
        Self {
            algorithm_version: "1.0.0".to_string(),
        }
    }

    pub fn find_matches(&self, learner: &User, mentors: &[Mentor], limit: usize) -> Vec<MatchResult> {
        let start_time = Instant::now();

        // Calculate compatibility scores for all mentor-learner pairs
        let mut compatibility_scores: Vec<(usize, f64, CompatibilityFactors)> = mentors
            .par_iter()
            .enumerate()
            .map(|(index, mentor)| {
                let score = self.calculate_compatibility_score(learner, mentor);
                let factors = self.calculate_compatibility_factors(learner, mentor);
                (index, score, factors)
            })
            .collect();

        // Sort by compatibility score (descending)
        compatibility_scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        // Take top matches
        let top_matches: Vec<MatchResult> = compatibility_scores
            .into_iter()
            .take(limit)
            .enumerate()
            .map(|(rank, (mentor_index, score, factors))| {
                let mentor = &mentors[mentor_index];
                MatchResult {
                    mentor_id: mentor.id,
                    score,
                    reasoning: self.generate_reasoning(&factors, rank + 1),
                    compatibility_factors: factors,
                }
            })
            .collect();

        let processing_time = start_time.elapsed();
        log::info!("Matching completed in {:?}", processing_time);

        top_matches
    }

    fn calculate_compatibility_score(&self, learner: &User, mentor: &Mentor) -> f64 {
        let factors = self.calculate_compatibility_factors(learner, mentor);

        // Weighted scoring algorithm
        let weights = CompatibilityWeights {
            skill_overlap: 0.4,
            location_match: 0.15,
            availability_match: 0.15,
            experience_compatibility: 0.15,
            teaching_style_match: 0.15,
        };

        let score = (factors.skill_overlap * weights.skill_overlap) +
                   ((factors.location_match as i32 as f64) * weights.location_match) +
                   (factors.availability_match * weights.availability_match) +
                   (factors.experience_compatibility * weights.experience_compatibility) +
                   (factors.teaching_style_match * weights.teaching_style_match);

        // Normalize to 0-100 scale
        (score * 100.0).min(100.0).max(0.0)
    }

    fn calculate_compatibility_factors(&self, learner: &User, mentor: &Mentor) -> CompatibilityFactors {
        CompatibilityFactors {
            skill_overlap: self.calculate_skill_overlap(&learner.skills, &mentor.expertise),
            location_match: self.calculate_location_match(&learner.location, &mentor.location),
            availability_match: self.calculate_availability_match(learner.availability, mentor.availability),
            experience_compatibility: self.calculate_experience_compatibility(learner.experience_level.as_str(), mentor.experience_years),
            teaching_style_match: self.calculate_teaching_style_match(learner, mentor),
        }
    }

    fn calculate_skill_overlap(&self, learner_skills: &[String], mentor_expertise: &[String]) -> f64 {
        if learner_skills.is_empty() || mentor_expertise.is_empty() {
            return 0.0;
        }

        let learner_set: std::collections::HashSet<_> = learner_skills.iter().collect();
        let mentor_set: std::collections::HashSet<_> = mentor_expertise.iter().collect();

        let intersection: std::collections::HashSet<_> = learner_set.intersection(&mentor_set).collect();
        let union = learner_set.len() + mentor_set.len() - intersection.len();

        if union == 0 {
            0.0
        } else {
            intersection.len() as f64 / union as f64
        }
    }

    fn calculate_location_match(&self, learner_location: &str, mentor_location: &str) -> bool {
        // Simple string matching - in production, use geocoding and distance calculation
        learner_location.to_lowercase() == mentor_location.to_lowercase() ||
        self.is_same_region(learner_location, mentor_location)
    }

    fn is_same_region(&self, loc1: &str, loc2: &str) -> bool {
        // Simplified region matching - expand based on your geographic needs
        let regions = [
            ("africa", ["nigeria", "kenya", "south africa", "ghana", "uganda"]),
            ("europe", ["uk", "germany", "france", "spain", "italy"]),
            ("asia", ["india", "china", "japan", "singapore"]),
            ("americas", ["usa", "canada", "brazil", "mexico"]),
        ];

        for (_, countries) in regions.iter() {
            let loc1_in_region = countries.iter().any(|&c| loc1.to_lowercase().contains(c));
            let loc2_in_region = countries.iter().any(|&c| loc2.to_lowercase().contains(c));
            if loc1_in_region && loc2_in_region {
                return true;
            }
        }

        false
    }

    fn calculate_availability_match(&self, learner_hours: i32, mentor_hours: i32) -> f64 {
        if mentor_hours == 0 {
            return 0.0;
        }

        let ratio = learner_hours as f64 / mentor_hours as f64;
        // Optimal match when learner needs <= mentor availability
        if ratio <= 1.0 {
            1.0
        } else {
            // Penalty for mentor being over-committed
            (1.0 / ratio).max(0.1)
        }
    }

    fn calculate_experience_compatibility(&self, learner_level: &str, mentor_years: i32) -> f64 {
        match learner_level.to_lowercase().as_str() {
            "beginner" => {
                // Beginners need patient mentors with good teaching skills
                if mentor_years >= 2 { 1.0 } else { 0.7 }
            },
            "intermediate" => {
                // Intermediates need mentors with relevant experience
                if mentor_years >= 3 { 1.0 } else if mentor_years >= 1 { 0.8 } else { 0.5 }
            },
            "advanced" => {
                // Advanced learners need highly experienced mentors
                if mentor_years >= 5 { 1.0 } else if mentor_years >= 3 { 0.8 } else { 0.6 }
            },
            _ => 0.5, // Default compatibility
        }
    }

    fn calculate_teaching_style_match(&self, learner: &User, mentor: &Mentor) -> f64 {
        // This is a simplified implementation
        // In production, you'd have learner preferences and mentor teaching styles
        match mentor.teaching_style.to_lowercase().as_str() {
            "structured" => {
                // Structured teaching works well for most learners
                0.9
            },
            "flexible" => {
                // Flexible teaching adapts to learner needs
                0.8
            },
            "hands-on" => {
                // Hands-on for practical learners
                if learner.learning_goals.iter().any(|goal| goal.to_lowercase().contains("project")) {
                    0.95
                } else {
                    0.7
                }
            },
            _ => 0.6, // Default compatibility
        }
    }

    fn generate_reasoning(&self, factors: &CompatibilityFactors, rank: usize) -> String {
        let mut reasons = Vec::new();

        if factors.skill_overlap > 0.7 {
            reasons.push("Excellent skill alignment".to_string());
        } else if factors.skill_overlap > 0.4 {
            reasons.push("Good skill overlap".to_string());
        }

        if factors.location_match {
            reasons.push("Location match".to_string());
        }

        if factors.availability_match > 0.8 {
            reasons.push("Availability compatibility".to_string());
        }

        if factors.experience_compatibility > 0.8 {
            reasons.push("Experience level match".to_string());
        }

        if reasons.is_empty() {
            format!("Rank {} match based on overall compatibility", rank)
        } else {
            format!("Rank {} match: {}", rank, reasons.join(", "))
        }
    }
}

struct CompatibilityWeights {
    skill_overlap: f64,
    location_match: f64,
    availability_match: f64,
    experience_compatibility: f64,
    teaching_style_match: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_skill_overlap_calculation() {
        let matcher = MentorMatcher::new();

        let learner_skills = vec!["python".to_string(), "django".to_string()];
        let mentor_expertise = vec!["python".to_string(), "rust".to_string()];

        let overlap = matcher.calculate_skill_overlap(&learner_skills, &mentor_expertise);
        assert_eq!(overlap, 1.0 / 3.0); // 1 intersection, 3 union
    }

    #[test]
    fn test_location_match() {
        let matcher = MentorMatcher::new();

        assert!(matcher.calculate_location_match("Nigeria", "Nigeria"));
        assert!(matcher.is_same_region("Kenya", "South Africa"));
        assert!(!matcher.is_same_region("Nigeria", "Germany"));
    }
}