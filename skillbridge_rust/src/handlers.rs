use actix_web::{web, HttpResponse, Result};
use serde_json::json;
use std::time::{Instant, SystemTime, UNIX_EPOCH};
use crate::models::{MatchingRequest, MatchingResponse, HealthCheck, MatchingStats};
use crate::matching::MentorMatcher;

static mut REQUEST_COUNT: u64 = 0;
static mut TOTAL_PROCESSING_TIME: u64 = 0;

pub async fn health_check() -> Result<HttpResponse> {
    let timestamp = chrono::Utc::now();

    let health = HealthCheck {
        status: "healthy".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        timestamp,
    };

    Ok(HttpResponse::Ok().json(health))
}

pub async fn match_mentors(req: web::Json<MatchingRequest>) -> Result<HttpResponse> {
    let start_time = Instant::now();
    let matcher = MentorMatcher::new();

    // Update request count (in production, use atomic operations)
    unsafe {
        REQUEST_COUNT += 1;
    }

    let limit = req.limit.unwrap_or(5).min(20); // Cap at 20 for performance

    log::info!("Processing matching request for {} mentors, limit: {}", req.mentors.len(), limit);

    // Perform matching
    let matches = matcher.find_matches(&req.learner, &req.mentors, limit);
    let matches_count = matches.len();

    let processing_time = start_time.elapsed().as_millis() as u64;

    // Update total processing time
    unsafe {
        TOTAL_PROCESSING_TIME += processing_time;
    }

    let response = MatchingResponse {
        matches,
        processing_time_ms: processing_time,
        algorithm_version: matcher.algorithm_version.clone(),
    };

    log::info!("Matching completed in {}ms, found {} matches", processing_time, matches_count);

    Ok(HttpResponse::Ok().json(response))
}

pub async fn get_matching_stats() -> Result<HttpResponse> {
    let uptime = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    unsafe {
        let request_count = REQUEST_COUNT;
        let avg_processing_time = if request_count > 0 {
            TOTAL_PROCESSING_TIME as f64 / request_count as f64
        } else {
            0.0
        };

        let stats = MatchingStats {
            total_requests: request_count,
            average_processing_time_ms: avg_processing_time,
            cache_hit_rate: 0.0, // Not implemented yet
            uptime_seconds: uptime,
        };

        Ok(HttpResponse::Ok().json(stats))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use actix_web::test;
    use crate::models::{User, Mentor};
    use uuid::Uuid;

    #[actix_web::test]
    async fn test_health_check() {
        let resp = health_check().await.unwrap();
        assert_eq!(resp.status(), 200);
    }

    #[actix_web::test]
    async fn test_matching_request() {
        let learner = User {
            id: Uuid::new_v4(),
            skills: vec!["python".to_string()],
            learning_goals: vec!["web development".to_string()],
            location: "Nigeria".to_string(),
            availability: 10,
            experience_level: "beginner".to_string(),
            preferred_languages: vec!["python".to_string()],
        };

        let mentor = Mentor {
            id: Uuid::new_v4(),
            expertise: vec!["python".to_string(), "django".to_string()],
            location: "Nigeria".to_string(),
            availability: 15,
            experience_years: 3,
            rating: 4.5,
            hourly_rate: 50,
            teaching_style: "structured".to_string(),
        };

        let request = MatchingRequest {
            learner,
            mentors: vec![mentor],
            limit: Some(5),
        };

        let req = test::TestRequest::post()
            .set_json(&request)
            .to_http_request();

        let resp = match_mentors(web::Json(request)).await.unwrap();
        assert_eq!(resp.status(), 200);
    }
}