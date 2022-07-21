# syntax=docker/dockerfile:1
FROM debian:stable-slim
WORKDIR /app
RUN mkdir logs
COPY target/release/nginx_logs .
#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["./nginx_logs", "logs"]
