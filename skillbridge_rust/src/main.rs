mod matching;
mod models;
mod handlers;

use actix_web::{web, App, HttpServer, middleware::Logger};
use actix_cors::Cors;
use env_logger::Env;
use std::env;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logger
    env_logger::init_from_env(Env::default().default_filter_or("info"));

    // Get port from environment or default to 8001
    let port = env::var("PORT").unwrap_or_else(|_| "8001".to_string());
    let address = format!("0.0.0.0:{}", port);

    log::info!("Starting SkillBridge Matching Service on {}", address);

    HttpServer::new(|| {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);

        App::new()
            .wrap(cors)
            .wrap(Logger::default())
            .route("/health", web::get().to(handlers::health_check))
            .route("/match", web::post().to(handlers::match_mentors))
            .route("/stats", web::get().to(handlers::get_matching_stats))
    })
    .bind(&address)?
    .run()
    .await
}