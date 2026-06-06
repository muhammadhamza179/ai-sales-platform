from typing import TypedDict, Optional, List, Dict

class AgentState(TypedDict):
    company_name: str
    linkedin_url: str
    screenshot_path: Optional[str]
    screenshot_base64: Optional[str]
    research_data: Optional[Dict]
    linkedin_data: Optional[Dict]
    visual_signals: Optional[Dict]
    company_alignment: Optional[Dict]
    persona: Optional[Dict]
    icp_score: Optional[str]
    icp_justification: Optional[str]
    closing_probability: Optional[int]
    sentiment_score: Optional[str]
    urgency_score: Optional[str]
    predicted_response_rate: Optional[str]
    email_drafts: Optional[List[Dict]]
    conversation_history: Optional[List[Dict]]
    objection_type: Optional[str]
    next_message: Optional[str]
    hubspot_contact_id: Optional[str]
    errors: List[str]
    job_id: str