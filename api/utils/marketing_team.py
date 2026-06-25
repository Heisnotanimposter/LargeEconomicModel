import os
import requests
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("MarketingTeam")

# Base class for Marketing Agents
class MarketingAgent:
    def __init__(self, name: str, role: str, instructions: str):
        self.name = name
        self.role = role
        self.instructions = instructions

    def generate(self, prompt: str, api_key: str = None) -> str:
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")

        if api_key and api_key != "PLACEHOLDER_API_KEY":
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                data = {
                    "contents": [{
                        "parts": [{
                            "text": f"{self.instructions}\n\nUser request: {prompt}"
                        }]
                    }]
                }
                response = requests.post(url, headers=headers, json=data, timeout=10)
                if response.status_code == 200:
                    resp_json = response.json()
                    return resp_json["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.warning(f"Gemini API returned status {response.status_code}. Using fallback.")
            except Exception as e:
                logger.error(f"Error querying Gemini API: {e}. Using fallback.")
        
        return self._fallback_generation(prompt)

    def _fallback_generation(self, prompt: str) -> str:
        raise NotImplementedError("Fallback must be implemented in sub-agents")


class StrategistAgent(MarketingAgent):
    def __init__(self):
        super().__init__(
            name="Campaign Strategist",
            role="Strategic lead defining target audiences and messaging matrices.",
            instructions="You are a senior tech growth advisor. Define target audiences, main messaging theme, and launch timeline for the given repo."
        )

    def _fallback_generation(self, prompt: str) -> str:
        p_lower = prompt.lower()
        if "zbdd" in p_lower or "solver" in p_lower:
            return """# Campaign Strategy: ZBDD-Solver Launch
## 1. Target Audience Segmentation
- **Tier 1: ML Researchers (PINN domain)**: Deep learning engineers integrating physics constraints. Main pain point: Training loops stalled by continuous boundary integrations.
- **Tier 2: Systems Optimization Devs**: C++/Rust engineers focusing on low-latency decision trees, SIMD/CUDA, memory layouts.
- **Tier 3: Quantitative Devs**: High-frequency trading researchers seeking ultra-fast combinatorial solvers.

## 2. Launch Timeline (72-Hour Star Lock-In)
- **Hour 0**: Repository Publication (Topics tagged, README optimized).
- **Hour 4**: Hacker News 'Show HN' Submission (Niche optimization focus).
- **Hour 12**: Reddit Segmentation Drop (r/MachineLearning & r/cpp).
- **Hour 24**: LinkedIn Network Routing loop via Simon Lee's profile.
- **Hour 48-72**: Issue Tracking & Pull Request feedback loop validation.
"""
        else:
            return """# Campaign Strategy: Large Economic Model (LEM) Launch
## 1. Target Audience Segmentation
- **Tier 1: Financial Analysts & Economists**: Data scientists needing rapid access to FRED, OECD, and IMF aggregates.
- **Tier 2: Python Web Developers**: Backend engineers building macroeconomic applications using FastAPI.
- **Tier 3: Streamlit / React Enthusiasts**: Developers looking for clean dashboard blueprints.

## 2. Launch Timeline (72-Hour Star Lock-In)
- **Hour 0**: Repository tagging & documentation check.
- **Hour 6**: Hacker News 'Show HN' Submission (Focus on single-point FRED/IMF aggregate API wrapper).
- **Hour 18**: Reddit Niche drops (r/dataisbeautiful & r/python).
- **Hour 36**: LinkedIn professional loop highlighting the live Streamlit demo.
"""


class CopywriterAgent(MarketingAgent):
    def __init__(self):
        super().__init__(
            name="Technical Copywriter",
            role="Copy lead drafting Hacker News submissions, Reddit posts, and LinkedIn hooks.",
            instructions="You are a senior technical writer. Draft high-impact, copy-pasteable HN Show comments, customized Reddit subreddit posts, and LinkedIn announcements."
        )

    def _fallback_generation(self, prompt: str) -> str:
        p_lower = prompt.lower()
        if "zbdd" in p_lower or "solver" in p_lower:
            return """# Launch Copywriting Assets: ZBDD-Solver

## 1. Hacker News Submission
- **Title**: `Show HN: ZBDD-Solver – Accelerating Discrete Optimization for Physics-Informed ML`
- **Comment Hook**:
  > Hi HN, we built ZBDD-Solver to solve discrete optimization boundaries inside Neural Network loss loops. By enforcing zero-suppression (ZBDD node pruning) to bypass inactive paths, we compressed constraint state spaces by 88% and lowered latency to ~48ms using SIMD/CUDA warp-level voting. No jump tables, no runtime memory allocations.

## 2. Reddit Segmentation Posts
### [Subreddit: r/MachineLearning]
- **Title**: `[P] ZBDD-Solver: Accelerating discrete constraint solving in PINNs by 15x`
- **Body**:
  > We open-sourced ZBDD-Solver, a C++/Python framework that maps sparse constraint boundary coordinates into Zero-Suppressed Decision Diagrams, allowing you to train boundary-constrained physics models without stalling on heavy MILP solvers like Gurobi.

### [Subreddit: r/cpp]
- **Title**: `[Showcase] Compiling sparse decision diagrams to SIMD/CUDA without branch redirection`
- **Body**:
  > We designed an MLIR compiler pass that flattens decision graphs into continuous registers, utilizing CUDA warp primitives (`__ballot_sync`) to evaluate Boolean constraint structures in parallel.

## 3. LinkedIn Status Hook (Simon Lee Profile)
> Can we speed up Physics-Informed Machine Learning by 15x using binary decision theory?
> 
> Continuous deep learning handles physical equations beautifully, but struggles with hard discrete boundaries. Instead of stalling models with heavy mathematical solvers, we compiled the constraint space into a hardware-accelerated Zero-Suppressed Binary Decision Diagram (ZBDD).
> 
> Check out the source code and give us a Star ⭐: https://github.com/yourusername/zbdd-solver
"""
        else:
            return """# Launch Copywriting Assets: Large Economic Model (LEM)

## 1. Hacker News Submission
- **Title**: `Show HN: A unified Economic Data API & Analysis platform (FRED, OECD, World Bank)`
- **Comment Hook**:
  > Hi HN, direct API integration with various economic databases is fragmented. We created a FastAPI-based server that indexes over 500 indicators across FRED, OECD, and IMF, featuring intelligent async caching, custom rate-limiting, and an interactive React dashboard.

## 2. Reddit Segmentation Posts
### [Subreddit: r/python]
- **Title**: `[Project] Open Source Economic API: Unified FastAPI wrapper for FRED, OECD, and World Bank`
- **Body**:
  > A clean Python engine using async client pools, sqlalchemy database layers, and BeautifulSoup indicators crawlers. Ready for developers needing direct macro data.

## 3. LinkedIn Status Hook (Simon Lee Profile)
> Fragmentation in economic data stops developers from building predictive tools.
> 
> We just open-sourced the Large Economic Model (LEM) Command Center, unifying FRED, World Bank, OECD, and IMF APIs under a high-performance FastAPI server and React/Next.js dashboard.
> 
> Explore the project: https://github.com/yourusername/LargeEconomicModel
"""


class SEOAgent(MarketingAgent):
    def __init__(self):
        super().__init__(
            name="SEO & Metadata Auditor",
            role="Audit lead optimizing repository tags and keywords to rank on GitHub search.",
            instructions="You are a GitHub SEO expert. List optimized topics, keywords, and README structure improvements for search discovery."
        )

    def _fallback_generation(self, prompt: str) -> str:
        p_lower = prompt.lower()
        if "zbdd" in p_lower or "solver" in p_lower:
            return """# GitHub SEO Audit: ZBDD-Solver
## 1. Recommended Repository Topics
- `physics-informed-ml`
- `cuda-acceleration`
- `compiler-optimization`
- `high-frequency-trading`
- `discrete-optimization`

## 2. Core Search Keywords
- "Zero-Suppressed Binary Decision Diagrams PINN"
- "LLVM MLIR decision diagram compiler"
- "Low latency CUDA discrete constraint solver"

## 3. README Metadata Improvements
- Add structured badges for python, license, CUDA, and LLVM/MLIR at the very top.
- Place the Mermaid diagram above the fold to capture visual interest in under 3 seconds.
"""
        else:
            return """# GitHub SEO Audit: Large Economic Model (LEM)
## 1. Recommended Repository Topics
- `economic-data-api`
- `fastapi-application`
- `macroeconomics`
- `fred-api`
- `data-visualization`

## 2. Core Search Keywords
- "unified economic data api python"
- "macroeconomic indicators dashboard react"
- "async FRED IMF OECD World Bank wrapper"

## 3. README Metadata Improvements
- Ensure streamlit demo link is at the top of the description.
- Include a quick start copy block using docker-compose up.
"""


class ResponderAgent(MarketingAgent):
    def __init__(self):
        super().__init__(
            name="Social Responder",
            role="Q&A agent specialized in drafting technical, convincing answers to user questions.",
            instructions="You are a senior tech advocate. Draft clear, polite, and technically precise answers to the user's critique or question regarding the project."
        )

    def _fallback_generation(self, prompt: str) -> str:
        p_lower = prompt.lower()
        if "gurobi" in p_lower or "milp" in p_lower or "solver" in p_lower:
            return """**Answer**: 
Gurobi and traditional MILP solvers are exact and extremely powerful for general constraints, but they operate as standalone CPUs or heavy runtime systems. In Physics-Informed ML, we evaluate constraints during every neural epoch (backpropagation step). Calling Gurobi via sub-processes millions of times stalls the GPU. 

ZBDD-Solver solves this by compiling the sparse constraint equations into a flat decision diagram directly lowered to CUDA warp registers. It evaluates constraints on the GPU in ~48ms without dynamic memory allocations, eliminating CPU-GPU communication overhead.
"""
        elif "economic" in p_lower or "fred" in p_lower or "api" in p_lower:
            return """**Answer**: 
FRED and the World Bank provide direct REST APIs, but each has separate rate limits, authentication schemes, schemas, and coordinate formats. 

LargeEconomicModel unifies all of them under a single async FastAPI engine, standardizes the response JSON structure (dates, countries, indicator names), and layers an intelligent SQLite/Redis caching layer. This allows you to build macro models or feed Streamlit/React frontends instantly without managing individual raw client connections.
"""
        else:
            return f"""**Answer**:
Thank you for the question! The project was built specifically to address the architectural complexity of this domain. We lower the state structures via custom JIT compiler blocks, bypassing dynamic memory allocation and minimizing CPU-GPU thread latency. Please check out our TECHNICAL_WHITEPAPER.md for the full mathematical derivations!
"""


# Orchestration class to represent the marketing team
class MarketingTeamManager:
    def __init__(self):
        self.strategist = StrategistAgent()
        self.copywriter = CopywriterAgent()
        self.seo = SEOAgent()
        self.responder = ResponderAgent()

    def run_campaign(self, project_name: str, project_desc: str, api_key: str = None) -> Dict[str, Any]:
        prompt = f"Project Name: {project_name}\nDescription: {project_desc}"
        
        # Run agents in sequence (Orchestration)
        strategy = self.strategist.generate(prompt, api_key)
        copy = self.copywriter.generate(prompt, api_key)
        seo = self.seo.generate(prompt, api_key)
        
        return {
            "project_name": project_name,
            "strategy": strategy,
            "copy": copy,
            "seo": seo
        }

    def simulate_qa(self, project_name: str, question: str, api_key: str = None) -> str:
        prompt = f"Project: {project_name}\nQuestion: {question}"
        return self.responder.generate(prompt, api_key)
