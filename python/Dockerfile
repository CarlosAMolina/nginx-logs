# syntax=docker/dockerfile:1
FROM python:3.11.3-alpine3.17
WORKDIR /app
COPY src/*.py src/
#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["python", "src/main.py", "logs"]
