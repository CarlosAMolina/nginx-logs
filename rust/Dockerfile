# syntax=docker/dockerfile:1

# Builder.
FROM rust:1.69.0-slim-buster AS builder
RUN rustup target add x86_64-unknown-linux-musl && \
    apt-get update && \
    apt-get install -y \
        --no-install-recommends\
        musl-tools \
        build-essential \
        cmake \
        && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY Cargo.lock .
COPY Cargo.toml .
COPY src/* src/
RUN cargo build --target x86_64-unknown-linux-musl --release

# Final image.
FROM alpine:3.17.3
WORKDIR /app
COPY --from=builder /app/target/x86_64-unknown-linux-musl/release/nginx_logs /app/
RUN ls -lh nginx_logs
#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["./nginx_logs", "logs"]
