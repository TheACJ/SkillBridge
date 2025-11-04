# Build stage
FROM rust:1.70-slim as builder

WORKDIR /app

# Copy manifest files
COPY Cargo.toml Cargo.lock ./

# Copy source code
COPY src ./src

# Build the application
RUN cargo build --release

# Runtime stage
FROM debian:bullseye-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -r -s /bin/false skillbridge

# Copy the binary from builder
COPY --from=builder /app/target/release/skillbridge-matching /usr/local/bin/

# Set ownership
RUN chown skillbridge:skillbridge /usr/local/bin/skillbridge-matching

# Switch to non-root user
USER skillbridge

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["skillbridge-matching"]