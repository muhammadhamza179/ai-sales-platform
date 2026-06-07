import time
import uuid
import os
import json
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from dotenv import load_dotenv
from api.models import ProspectResponse, HealthResponse
from agent.graph import create_graph
from utils.image_processor import process_image
from agent.nodes import safe_json_parse
from langchain_core.messages import HumanMessage, SystemMessage
from agent.prompts import OBJECTION_HANDLING_PROMPT
from groq import Groq

load_dotenv()

router = APIRouter()
graph = create_graph()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        message="AI Sales Platform is running",
        version="1.0.0"
    )


@router.post("/analyze", response_model=ProspectResponse)
async def analyze_prospect(
    company_name: str = Form(...),
    linkedin_url: str = Form(...),
    screenshot: Optional[UploadFile] = File(None)
):
    job_id = str(uuid.uuid4())
    screenshot_base64 = None

    if screenshot and screenshot.filename:
        contents = await screenshot.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Screenshot must be under 5MB")
        try:
            screenshot_base64 = process_image(contents)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    initial_state = {
        "company_name": company_name,
        "linkedin_url": linkedin_url,
        "screenshot_path": None,
        "screenshot_base64": screenshot_base64,
        "research_data": None,
        "linkedin_data": None,
        "visual_signals": None,
        "company_alignment": None,
        "persona": None,
        "icp_score": None,
        "icp_justification": None,
        "closing_probability": None,
        "sentiment_score": None,
        "urgency_score": None,
        "predicted_response_rate": None,
        "email_drafts": None,
        "conversation_history": [],
        "objection_type": None,
        "next_message": None,
        "hubspot_contact_id": None,
        "errors": [],
        "job_id": job_id
    }

    start = time.time()
    result = graph.invoke(initial_state)
    elapsed = round(time.time() - start, 2)

    return ProspectResponse(
        job_id=job_id,
        company_name=company_name,
        status="completed",
        total_time_seconds=elapsed,
        sources_found=result.get("research_data", {}).get("sources_count", 0),
        industry=result.get("research_data", {}).get("industry", "unknown"),
        funding_stage=result.get("research_data", {}).get("funding_stage", "unknown"),
        persona=result.get("persona", {}).get("job_title", "unknown"),
        closing_probability=result.get("closing_probability", 0),
        sentiment_score=result.get("sentiment_score", "unknown"),
        urgency_score=result.get("urgency_score", "unknown"),
        predicted_response_rate=result.get("predicted_response_rate", "unknown"),
        icp_score=result.get("icp_score", "unknown"),
        strongest_alignment=result.get("company_alignment", {}).get("strongest_alignment", ""),
        email_drafts=result.get("email_drafts", []),
        hubspot_contact_id=result.get("hubspot_contact_id"),
        visual_key_insight=result.get("visual_signals", {}).get("key_insight", "No screenshot provided"),
        errors=result.get("errors", [])
    )


@router.post("/continue-conversation")
async def continue_conversation(
    company_name: str = Form(...),
    prospect_reply: str = Form(...),
    conversation_history: str = Form("[]"),
    closing_probability: int = Form(50)
):
    try:
        history = json.loads(conversation_history)
    except Exception:
        history = []

    # Use Groq for objection handling (free, fast, already working)
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    GROQ_MODEL = "llama-3.3-70b-versatile"

    context = f"""Company: {company_name}
Prospect Reply: {prospect_reply}
Current Closing Probability: {closing_probability}%
Conversation History: {json.dumps(history, indent=2)}
"""
    full_prompt = f"{OBJECTION_HANDLING_PROMPT}\n\n{context}"

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.3,
        max_tokens=1000
    )
    
    result = safe_json_parse(response.choices[0].message.content)

    return JSONResponse(content={
        "objection_type": result.get("objection_type", "unknown"),
        "response": result.get("response", ""),
        "closing_probability_update": result.get("closing_probability_update", closing_probability),
        "recommended_next_action": result.get("recommended_next_action", "")
    })