from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid


class ProspectRequest(BaseModel):
    company_name: str
    linkedin_url: str
    job_id: Optional[str] = None

    def __init__(self, **data):
        if not data.get("job_id"):
            data["job_id"] = str(uuid.uuid4())
        super().__init__(**data)


class EmailDraft(BaseModel):
    subject: Optional[str] = ""
    body: Optional[str] = ""


class ProspectResponse(BaseModel):
    job_id: str
    company_name: str
    status: str
    total_time_seconds: Optional[float] = None
    sources_found: Optional[int] = None
    industry: Optional[str] = None
    funding_stage: Optional[str] = None
    persona: Optional[str] = None
    closing_probability: Optional[int] = None
    sentiment_score: Optional[str] = None
    urgency_score: Optional[str] = None
    predicted_response_rate: Optional[str] = None
    icp_score: Optional[str] = None
    strongest_alignment: Optional[str] = None
    email_drafts: Optional[List[Dict]] = None
    hubspot_contact_id: Optional[str] = None
    visual_key_insight: Optional[str] = None
    errors: Optional[List[str]] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    message: str
    version: str