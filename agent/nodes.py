import os
import json
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from groq import Groq
from agent.state import AgentState
from agent.prompts import (
    RESEARCH_SUMMARY_PROMPT,
    VISION_ANALYSIS_PROMPT,
    LINKEDIN_ANALYSIS_PROMPT,
    PERSONA_SCORING_PROMPT,
    ALIGNMENT_PROMPT,
    THREE_MESSAGE_PROMPT,
    OBJECTION_HANDLING_PROMPT
)

load_dotenv()

# Initialize Tavily
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Initialize Groq client (free, fast, no rate limit issues)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Use Llama 3.3 70B (free, very capable)
GROQ_MODEL = "llama-3.3-70b-versatile"


def call_groq(prompt: str) -> str:
    """Simple wrapper to call Groq API"""
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq API error: {e}")
        raise


def safe_json_parse(text: str) -> dict:
    try:
        clean = text.strip()
        if "```" in clean:
            parts = clean.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    clean = part[4:].strip()
                    break
                elif part.startswith("{"):
                    clean = part
                    break
        if not clean.startswith("{"):
            start = clean.find("{")
            end = clean.rfind("}") + 1
            if start != -1 and end != 0:
                clean = clean[start:end]
        return json.loads(clean)
    except Exception as e:
        return {"error": str(e), "raw": text[:200]}


def research_node(state: AgentState) -> AgentState:
    print(f"[research] Researching {state['company_name']}")
    errors = state.get("errors", [])
    try:
        company = state["company_name"]
        queries = [
            f"{company} company overview funding 2025 2026",
            f"{company} product tech stack engineering team",
            f"{company} recent news growth hiring customers"
        ]
        raw_results = []
        for query in queries:
            response = tavily.search(query=query, max_results=3)
            raw_results.extend(response.get("results", []))
        sources_text = "\n\n".join([
            f"Title: {r.get('title', '')}\nContent: {r.get('content', '')[:400]}"
            for r in raw_results
        ])
        
        full_prompt = f"{RESEARCH_SUMMARY_PROMPT}\n\nCompany: {company}\n\nSearch Results:\n{sources_text}"
        response_text = call_groq(full_prompt)
        research_data = safe_json_parse(response_text)
        research_data["sources_count"] = len(raw_results)
        print(f"[research] Done. {len(raw_results)} sources found.")
        return {**state, "research_data": research_data, "errors": errors}
    except Exception as e:
        error_msg = f"research_node failed: {str(e)}"
        print(f"[research] ERROR: {error_msg}")
        return {**state, "research_data": {"sources_count": 0}, "errors": errors + [error_msg]}


def linkedin_node(state: AgentState) -> AgentState:
    print(f"[linkedin] Analyzing LinkedIn data")
    errors = state.get("errors", [])
    try:
        api_key = os.getenv("PROXYCURL_API_KEY")
        url = state.get("linkedin_url", "")
        if not url or not api_key or api_key == "skip":
            print(f"[linkedin] Skipping, no valid API key")
            return {**state, "linkedin_data": {"skipped": True}, "errors": errors}
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"linkedin_company_url": url}
        response = requests.get(
            "https://nubela.co/proxycurl/api/linkedin/company",
            headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code != 200:
            return {**state, "linkedin_data": {"skipped": True}, "errors": errors}
        company_data = response.json()
        summary_text = f"""
Company: {company_data.get('name', '')}
Description: {company_data.get('description', '')[:500]}
Industry: {company_data.get('industry', '')}
Size: {company_data.get('company_size_on_linkedin', '')}
Specialities: {', '.join(company_data.get('specialities', [])[:5])}
"""
        full_prompt = f"{LINKEDIN_ANALYSIS_PROMPT}\n\n{summary_text}"
        response_text = call_groq(full_prompt)
        linkedin_data = safe_json_parse(response_text)
        print(f"[linkedin] Done.")
        return {**state, "linkedin_data": linkedin_data, "errors": errors}
    except Exception as e:
        error_msg = f"linkedin_node failed: {str(e)}"
        print(f"[linkedin] ERROR: {error_msg}")
        return {**state, "linkedin_data": {"skipped": True}, "errors": errors + [error_msg]}


def vision_node(state: AgentState) -> AgentState:
    print(f"[vision] Analyzing screenshot")
    errors = state.get("errors", [])
    if not state.get("screenshot_base64"):
        print(f"[vision] No screenshot provided, skipping")
        return {**state, "visual_signals": {"skipped": True}, "errors": errors}
    try:
        full_prompt = f"{VISION_ANALYSIS_PROMPT}\n\nAnalyze this screenshot for the company: {state['company_name']}"
        response_text = call_groq(full_prompt)
        visual_signals = safe_json_parse(response_text)
        print(f"[vision] Done.")
        return {**state, "visual_signals": visual_signals, "errors": errors}
    except Exception as e:
        error_msg = f"vision_node failed: {str(e)}"
        print(f"[vision] ERROR: {error_msg}")
        return {**state, "visual_signals": {"skipped": True}, "errors": errors + [error_msg]}


def persona_scoring_node(state: AgentState) -> AgentState:
    print(f"[persona_scoring] Calculating scores")
    errors = state.get("errors", [])
    try:
        context = f"""
Research Data: {json.dumps(state.get('research_data', {}), indent=2)}
Visual Signals: {json.dumps(state.get('visual_signals', {}), indent=2)}
LinkedIn Data: {json.dumps(state.get('linkedin_data', {}), indent=2)}
Company: {state['company_name']}
"""
        full_prompt = f"{PERSONA_SCORING_PROMPT}\n\n{context}"
        response_text = call_groq(full_prompt)
        scoring = safe_json_parse(response_text)
        closing_prob = scoring.get("closing_probability", 0)
        icp = "high" if closing_prob >= 70 else "medium" if closing_prob >= 40 else "low"
        print(f"[persona_scoring] Done. Closing probability: {closing_prob}%")
        return {
            **state,
            "persona": scoring,
            "icp_score": icp,
            "icp_justification": f"{scoring.get('sentiment_score', '')} sentiment, {scoring.get('urgency_score', '')} urgency",
            "closing_probability": closing_prob,
            "sentiment_score": scoring.get("sentiment_score", "neutral"),
            "urgency_score": scoring.get("urgency_score", "medium"),
            "predicted_response_rate": scoring.get("predicted_response_rate", "10 to 20 percent"),
            "errors": errors
        }
    except Exception as e:
        error_msg = f"persona_scoring_node failed: {str(e)}"
        print(f"[persona_scoring] ERROR: {error_msg}")
        return {**state, "persona": {}, "closing_probability": 0, "errors": errors + [error_msg]}


def alignment_node(state: AgentState) -> AgentState:
    print(f"[alignment] Finding company alignment")
    errors = state.get("errors", [])
    try:
        from utils.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        query = f"{state['company_name']} {state.get('research_data', {}).get('industry', '')} {state.get('research_data', {}).get('pain_points', [])}"
        relevant_docs = kb.search(query=query, n_results=3)
        context = f"""
Prospect Research: {json.dumps(state.get('research_data', {}), indent=2)}
Prospect Persona: {json.dumps(state.get('persona', {}), indent=2)}
Our Company Knowledge Base:
{relevant_docs}
"""
        full_prompt = f"{ALIGNMENT_PROMPT}\n\n{context}"
        response_text = call_groq(full_prompt)
        alignment = safe_json_parse(response_text)
        print(f"[alignment] Done.")
        return {**state, "company_alignment": alignment, "errors": errors}
    except Exception as e:
        error_msg = f"alignment_node failed: {str(e)}"
        print(f"[alignment] ERROR: {error_msg}")
        return {**state, "company_alignment": {}, "errors": errors + [error_msg]}


def outreach_node(state: AgentState) -> AgentState:
    print(f"[outreach] Generating three message sequence")
    errors = state.get("errors", [])
    try:
        context = f"""
Company: {state['company_name']}
Research: {json.dumps(state.get('research_data', {}), indent=2)}
Visual Signals: {json.dumps(state.get('visual_signals', {}), indent=2)}
LinkedIn Data: {json.dumps(state.get('linkedin_data', {}), indent=2)}
Persona: {json.dumps(state.get('persona', {}), indent=2)}
Company Alignment: {json.dumps(state.get('company_alignment', {}), indent=2)}
Closing Probability: {state.get('closing_probability', 0)}%
Sentiment: {state.get('sentiment_score', 'neutral')}
"""
        full_prompt = f"{THREE_MESSAGE_PROMPT}\n\n{context}"
        response_text = call_groq(full_prompt)
        result = safe_json_parse(response_text)
        email_drafts = [
            result.get("message_1", {}),
            result.get("message_2", {}),
            result.get("message_3", {})
        ]
        print(f"[outreach] Done. Three messages generated.")
        return {**state, "email_drafts": email_drafts, "errors": errors}
    except Exception as e:
        error_msg = f"outreach_node failed: {str(e)}"
        print(f"[outreach] ERROR: {error_msg}")
        return {**state, "email_drafts": [], "errors": errors + [error_msg]}


def crm_node(state: AgentState) -> AgentState:
    print(f"[crm] Writing to HubSpot")
    errors = state.get("errors", [])
    try:
        from utils.hubspot_client import HubSpotClient
        client = HubSpotClient()
        contact_id = client.create_contact(
            company_name=state["company_name"],
            linkedin_url=state["linkedin_url"],
            icp_score=state.get("icp_score", "unknown"),
            persona_title=state.get("persona", {}).get("job_title", "unknown"),
            closing_probability=state.get("closing_probability", 0)
        )
        note = f"""
AI Sales Platform Analysis
Company: {state['company_name']}
Closing Probability: {state.get('closing_probability', 0)}%
ICP Score: {state.get('icp_score', 'unknown')}
Sentiment: {state.get('sentiment_score', 'unknown')}
Urgency: {state.get('urgency_score', 'unknown')}
Predicted Response Rate: {state.get('predicted_response_rate', 'unknown')}
Persona: {state.get('persona', {}).get('job_title', 'unknown')}
Strongest Alignment: {state.get('company_alignment', {}).get('strongest_alignment', 'none')}
Key Visual Insight: {state.get('visual_signals', {}).get('key_insight', 'no screenshot provided')}
Sources Researched: {state.get('research_data', {}).get('sources_count', 0)}
"""
        client.create_note(contact_id=contact_id, content=note)
        print(f"[crm] Done. HubSpot ID: {contact_id}")
        return {**state, "hubspot_contact_id": contact_id, "errors": errors}
    except Exception as e:
        error_msg = f"crm_node failed: {str(e)}"
        print(f"[crm] ERROR: {error_msg}")
        return {**state, "hubspot_contact_id": None, "errors": errors + [error_msg]}