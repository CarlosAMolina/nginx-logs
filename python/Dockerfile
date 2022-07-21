# syntax=docker/dockerfile:1
FROM python:3.9.13-alpine3.16
WORKDIR /app
RUN mkdir logs
COPY src/*.py src/
ENTRYPOINT ["tail", "-f", "/dev/null"]
#ENTRYPOINT ["ls"]
#CMD ["logs"]
