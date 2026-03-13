# LEM (Large Economic Model) Architecture

## Brand Identity

**Name**: Large Economic Model (LEM)  
**Visual language**: High-contrast monotone  
**Colors**:
- Obsidian Black `#0A0A0A` — background
- Pure White `#FFFFFF` — data points
- Silver Gray `#A1A1AA` — secondary text

**Typography**:
- Geist Mono — data values (precision)
- Geist Sans — UI elements
- Tight tracking, bold weights for headers

---

## Project Structure

```
large-economic-model/
├── web-lem/                 # The Command Center (Next.js 14)
│   ├── src/app/             # App Router, Server Components
│   └── components/          # Geist Mono, Geist Sans
├── api-lem/                 # The LEM Engine (FastAPI)
│   ├── core/                # uvloop, orjson, L1/L2 cache, resilience
│   └── (uses api/ for routers, providers)
└── infrastructure/          # Docker, Nginx
    ├── docker-compose.lem.yml
    ├── Dockerfile.api-lem
    ├── Dockerfile.web-lem
    └── nginx.lem.conf
```

---

## The Command Center (web-lem)

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS — LEM-Dark theme
- **Charts**: Nivo — 1px lines, 10%→0% area gradients
- **Transitions**: Framer Motion — fade-in on data load
- **Components**: shadcn/ui style — sharp edges (no rounded corners)

---

## The LEM Engine (api-lem)

- **Serialization**: ORJSONResponse for large JSON payloads
- **Event loop**: uvloop (Unix)
- **L1 cache**: In-memory, 60s TTL (market data)
- **L2 cache**: Redis, 1hr TTL (historical indicators)
- **Resilience**: Timeout + retry patterns for external providers
- **Routers**: Reuses `api/` routers and providers

---

## Infrastructure

- **Docker Compose**: api-lem, web-lem, Redis, Nginx
- **Nginx**: Reverse proxy, SSL/HTTP2 ready

---

## Quick Start

```bash
# LEM Engine
cd api-lem && pip install -r requirements.txt
uvicorn api_lem.main:app --reload

# Command Center
cd web-lem && npm run dev

# Full stack
cd infrastructure && docker compose -f docker-compose.lem.yml up -d
```
