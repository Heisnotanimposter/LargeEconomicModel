from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from api.utils.marketing_team import MarketingTeamManager

router = APIRouter()
team_manager = MarketingTeamManager()

class CampaignRequest(BaseModel):
    project_name: str
    project_desc: str
    api_key: Optional[str] = None

class QARequest(BaseModel):
    project_name: str
    question: str
    api_key: Optional[str] = None

@router.get("/agents", tags=["Marketing Team"])
async def get_agents():
    """Get the active Marketing Team agents, roles, and status"""
    return {
        "agents": [
            {
                "id": "strategist",
                "name": team_manager.strategist.name,
                "role": team_manager.strategist.role,
                "status": "idle"
            },
            {
                "id": "copywriter",
                "name": team_manager.copywriter.name,
                "role": team_manager.copywriter.role,
                "status": "idle"
            },
            {
                "id": "seo",
                "name": team_manager.seo.name,
                "role": team_manager.seo.role,
                "status": "idle"
            },
            {
                "id": "responder",
                "name": team_manager.responder.name,
                "role": team_manager.responder.role,
                "status": "idle"
            }
        ]
    }

@router.post("/campaigns", tags=["Marketing Team"])
async def run_campaign(request: CampaignRequest):
    """Run agent loops to generate marketing strategies and copywriting copy"""
    if not request.project_name.strip() or not request.project_desc.strip():
        raise HTTPException(status_code=400, detail="Project name and description are required")
    
    try:
        results = team_manager.run_campaign(
            project_name=request.project_name,
            project_desc=request.project_desc,
            api_key=request.api_key
        )
        return {
            "status": "success",
            "campaign": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed running campaign agents: {str(e)}")

@router.post("/simulate-qa", tags=["Marketing Team"])
async def simulate_qa(request: QARequest):
    """Simulate a question from the community and generate the Social Responder's response"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
        
    try:
        answer = team_manager.simulate_qa(
            project_name=request.project_name,
            question=request.question,
            api_key=request.api_key
        )
        return {
            "status": "success",
            "question": request.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed simulating Q&A: {str(e)}")
