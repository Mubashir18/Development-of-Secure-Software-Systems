# PostgreSQL Task 1 - Database Connection Application

## Task Requirements
- Install PostgreSQL 16/17 (using Docker)
- Create database with locale `ru_RU.UTF-8`
- Create user with USAGE access only
- Develop app that:
  - Reads connection settings from config file
  - Gets credentials from user
  - Securely combines both
  - Executes `SELECT VERSION()`

## Docker Setup

### Build and Run
```bash
# Method 1: Using docker-compose (recommended)
docker-compose up -d

# Method 2: Using Docker directly
docker build -t task1-postgres .
docker run -d --name task1-postgres -p 5432:5432 task1-postgres