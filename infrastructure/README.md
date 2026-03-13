# LEM Infrastructure

Docker and Nginx configuration for **Large Economic Model (LEM)**.

## Layout

- `docker-compose.lem.yml` — LEM stack (api-lem, web-lem, Redis, Nginx)
- `Dockerfile.api-lem` — LEM Engine (FastAPI, uvloop, ORJSON)
- `Dockerfile.web-lem` — LEM Command Center (Next.js 14)
- `nginx.lem.conf` — Reverse proxy, SSL/HTTP2 ready

## Quick Start

```bash
# From project root
cd infrastructure
docker compose -f docker-compose.lem.yml up -d

# API: http://localhost:8000
# Web: http://localhost:3000
# Nginx: http://localhost:80 (proxies to API and Web)
```

## Services

| Service  | Port | Description                    |
|----------|------|--------------------------------|
| api-lem  | 8000 | LEM Engine (FastAPI)           |
| web-lem  | 3000 | Command Center (Next.js)       |
| redis    | 6379 | L2 cache                       |
| nginx    | 80   | Reverse proxy                  |

## Environment

Create `../.env` with:

```
REDIS_URL=redis://redis:6379/0
FRED_API_KEY=...
NEXT_PUBLIC_API_URL=http://api-lem:8000
```
