# PostgreSQL Pinger Application

This application periodically checks the connection to a PostgreSQL database and logs the results.

## Features
- Pings PostgreSQL every N seconds (set via `PING_INTERVAL`)
- Logs successful and failed connections
- Detects atypical PostgreSQL versions
- Does not freeze on connection failure
- Can duplicate logs to a file via `LOG_FILE` env variable
- Fully Dockerized setup

## Run with Docker Compose
1. Clone this repository
2. Build and start:
   ```bash
   docker compose --env-file .env up --build