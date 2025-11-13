use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: Uuid,
    pub skills: Vec<String>,
    pub learning_goals: Vec<String>,
    pub location: String,
    pub availability: i32, // hours per week
    pub experience_level: String,
    pub preferred_languages: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Mentor {
    pub id: Uuid,
    pub expertise: Vec<String>,
    pub location: String,
    pub availability: i32,
    pub experience_years: i32,
    pub rating: f64,
    pub hourly_rate: i32,
    pub teaching_style: String,
    // TODO: Expand
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatchResult {
    pub mentor_id: Uuid,
    pub score: f64,
    pub reasoning: String,
    pub compatibility_factors: CompatibilityFactors,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompatibilityFactors {
    pub skill_overlap: f64,
    pub location_match: bool,
    pub availability_match: f64,
    pub experience_compatibility: f64,
    pub teaching_style_match: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MatchingRequest {
    pub learner: User,
    pub mentors: Vec<Mentor>,
    pub limit: Option<usize>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MatchingResponse {
    pub matches: Vec<MatchResult>,
    pub processing_time_ms: u64,
    pub algorithm_version: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HealthCheck {
    pub status: String,
    pub version: String,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MatchingStats {
    pub total_requests: u64,
    pub average_processing_time_ms: f64,
    pub cache_hit_rate: f64,
    pub uptime_seconds: u64,
}