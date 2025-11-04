# SkillBridge Matching Service

A high-performance Rust microservice for intelligent mentor-learner matching in the SkillBridge platform.

## Features

- **Intelligent Matching Algorithm**: Multi-factor compatibility scoring using skill overlap, location, availability, experience level, and teaching style
- **High Performance**: Built with Rust for low latency and high throughput
- **Parallel Processing**: Uses Rayon for concurrent matching calculations
- **RESTful API**: Clean HTTP API with JSON responses
- **Health Monitoring**: Built-in health checks and performance metrics
- **Docker Ready**: Containerized deployment with multi-stage builds

## API Endpoints

### POST /match
Find best mentor matches for a learner.

**Request Body:**
```json
{
  "learner": {
    "id": "uuid",
    "skills": ["python", "django"],
    "learning_goals": ["web development"],
    "location": "Nigeria",
    "availability": 10,
    "experience_level": "beginner",
    "preferred_languages": ["python"]
  },
  "mentors": [
    {
      "id": "uuid",
      "expertise": ["python", "django"],
      "location": "Nigeria",
      "availability": 15,
      "experience_years": 3,
      "rating": 4.5,
      "hourly_rate": 50,
      "teaching_style": "structured"
    }
  ],
  "limit": 5
}
```

**Response:**
```json
{
  "matches": [
    {
      "mentor_id": "uuid",
      "score": 85.5,
      "reasoning": "Rank 1 match: Excellent skill alignment, Location match",
      "compatibility_factors": {
        "skill_overlap": 0.8,
        "location_match": true,
        "availability_match": 0.9,
        "experience_compatibility": 0.7,
        "teaching_style_match": 0.8
      }
    }
  ],
  "processing_time_ms": 45,
  "algorithm_version": "1.0.0"
}
```

### GET /health
Health check endpoint.

### GET /stats
Service performance statistics.

## Algorithm Overview

The matching algorithm uses a weighted scoring system with the following factors:

1. **Skill Overlap (40%)**: Jaccard similarity between learner skills and mentor expertise
2. **Location Match (15%)**: Binary score for same location/region
3. **Availability Match (15%)**: Compatibility between learner needs and mentor availability
4. **Experience Compatibility (15%)**: Mentor experience appropriateness for learner level
5. **Teaching Style Match (15%)**: Compatibility between learner preferences and mentor style

## Development

### Prerequisites
- Rust 1.70+
- Docker (optional)

### Local Development
```bash
# Clone and build
cargo build

# Run tests
cargo test

# Run with logging
RUST_LOG=info cargo run
```

### Docker Development
```bash
# Build and run
docker-compose up --build

# Run tests in container
docker-compose exec skillbridge-matching cargo test
```

## Performance

- **Latency**: < 50ms for typical matching requests (1 learner, 10-20 mentors)
- **Throughput**: 1000+ requests/second on modern hardware
- **Memory**: ~50MB base memory usage
- **CPU**: Efficient parallel processing with Rayon

## Deployment

### Docker
```bash
docker build -t skillbridge-matching .
docker run -p 8001:8001 skillbridge-matching
```

### Kubernetes
Use the provided docker-compose.yml as a reference for K8s deployment with resource limits and health checks.

## Configuration

Environment variables:
- `PORT`: Service port (default: 8001)
- `RUST_LOG`: Log level (default: info)

## Testing

```bash
# Unit tests
cargo test

# Integration tests
cargo test --test integration

# Benchmarks
cargo bench
```

## Monitoring

- Health endpoint: `GET /health`
- Metrics endpoint: `GET /stats`
- Structured logging with request IDs
- Performance monitoring built-in

## Contributing

1. Follow Rust best practices
2. Add tests for new features
3. Update documentation
4. Use conventional commits

## License

MIT License