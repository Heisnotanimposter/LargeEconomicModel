#  Economic Agent - Economic Sector Specialization

This document describes the ** agentic framework** integration specialized for the **economic sector** within the LargeEconomicModel project.

##  Agentic Code - Use Cases

### What is ?

**** ( Wiggum technique) is an autonomous AI agent loop where:

1. The AI agent receives a task
2. It executes tools, gathers data, and works toward completion
3. A `verifyCompletion` function checks if the task is done
4. If not complete, the agent runs another iteration with feedback
5. Loop continues until verified complete or a safety limit is reached

**Core concept**: `while (true)` for AI — the agent keeps trying until the job is done.

###  Use Cases

| Use Case | Description |
|----------|-------------|
| **Enterprise workflow automation** | Overnight task completion without manual intervention |
| **Complex multi-step processes** | Autonomous execution across interfaces |
| **Spec-driven development** | AI builds applications from requirements/PRDs |
| **Code migrations** | Jest→Vitest, CJS→ESM, dependency upgrades |
| **Data analysis** | Fetch data, analyze, iterate until insights are complete |
| **Report generation** | Gather data, compute, format, verify completeness |

### Economic Sector Specialization

Our ** Economic Agent** applies this pattern to economic research:

- **Data gathering**: Fetch GDP, inflation, unemployment, etc. from the Economic Data API
- **Cross-country comparison**: Compare indicators across countries
- **Analytics**: Compute statistics, trends, correlations
- **Report generation**: Produce structured economic analysis
- **Verification**: Ensure all requested data and analysis are present before finishing

## Repository Layout

```
LargeEconomicModel/
├── -loop-agent/              # Cloned from vercel-labs/-loop-agent
│   ├── packages/
│   │   └── -loop-agent/      # Core framework
│   ├── examples/
│   │   ├── cli/                   # General coding agent (sandbox)
│   │   └── economic-agent/        # Economic sector specialization
│   │       ├── index.ts           # Agent entry point
│   │       ├── ECONOMIC_INSTRUCTIONS.md
│   │       ├── lib/tools/economic.ts   # Economic data tools
│   │       └── README.md
│   └── package.json
└── api/                           # Economic Data API (data source)
```

## Quick Start

### 1. Clone  (Already Done)

```bash
cd /Users/seungwonlee/LargeEconomicModel
git clone https://github.com/vercel-labs/-loop-agent.git -loop-agent
```

### 2. Start the Economic Data API

```bash
./start_api.sh
# API runs at http://localhost:8000
```

### 3. Install & Run the Economic Agent

```bash
cd -loop-agent

# Install (requires pnpm - install via: npm install -g pnpm)
pnpm install
pnpm build

# Run economic agent
pnpm examples:economic "Compare unemployment rates in USA, GBR, and DEU from 2020"
```

### 4. Environment Variables

Create `-loop-agent/.env` or export:

```bash
# LLM provider (one required)
export ANTHROPIC_API_KEY=your_key    # For Claude
# or
export OPENAI_API_KEY=your_key       # For GPT-4

# Economic API (optional - defaults to localhost:8000)
export ECONOMIC_API_URL=http://localhost:8000
```

## Economic Agent Tools

| Tool | Purpose |
|------|---------|
| `fetchEconomicIndicator` | Get GDP, inflation, unemployment, etc. for a country |
| `compareCountries` | Compare an indicator across 2–10 countries |
| `getEconomicSummary` | Overview of key metrics for a country |
| `calculateAnalytics` | Mean, median, std, trend over a date range |
| `calculateCorrelation` | Correlation between two indicators |
| `listAvailableData` | List countries and indicators |
| `getMarketData` | Stock indices, FX rates, commodities |

## Example Prompts

```bash
# Cross-country comparison
pnpm examples:economic "Compare GDP growth in USA, China, and Germany from 2020 to 2024"

# Trend analysis
pnpm examples:economic "Analyze unemployment trend in France over the last 5 years"

# Correlation
pnpm examples:economic "Find correlation between inflation and interest rates in the UK"

# Regional summary
pnpm examples:economic "Economic summary for Brazil, Argentina, and Chile"
```

## How It Integrates

```
User Prompt
    ↓
 Economic Agent (loop)
    ↓
Economic Tools ──→ Economic Data API (localhost:8000)
    ↓                    ↓
    ↓              FRED, World Bank, OECD, IMF
    ↓
verifyCompletion ──→ Complete? → Output
    ↓                    ↓
    No → Next iteration
```

## Customization

- **Instructions**: Edit `-loop-agent/examples/economic-agent/ECONOMIC_INSTRUCTIONS.md`
- **Tools**: Add or modify tools in `lib/tools/economic.ts`
- **Verification**: Adjust `verifyCompletion` in `index.ts`
- **Stop limit**: Change `iterationCountIs(15)` in `index.ts`

## References

- [-loop-agent](https://github.com/vercel-labs/-loop-agent) - Vercel Labs implementation
- [Getting Started with ](https://www.aihero.dev/getting-started-with-)
- [Economic Data API](./API_README.md) - Our data provider
