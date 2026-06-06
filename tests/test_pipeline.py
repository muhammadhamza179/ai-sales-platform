import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
import time
import uuid
from agent.graph import create_graph

def test_full_pipeline():
    graph = create_graph()
    initial_state = {
        "company_name": "Notion",
        "linkedin_url": "https://linkedin.com/company/notionhq",
        "screenshot_path": None,
        "screenshot_base64": None,
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
        "job_id": str(uuid.uuid4())
    }

    print("\n=== STARTING FULL PIPELINE TEST ===\n")
    start = time.time()
    result = graph.invoke(initial_state)
    elapsed = round(time.time() - start, 2)

    print("\n=== FINAL RESULTS ===\n")
    print(f"Total time: {elapsed} seconds")
    print(f"Sources found: {result['research_data'].get('sources_count', 0)}")
    print(f"Industry detected: {result['research_data'].get('industry', 'unknown')}")
    print(f"Funding stage: {result['research_data'].get('funding_stage', 'unknown')}")
    print(f"Persona: {result.get('persona', {}).get('job_title', 'unknown')}")
    print(f"Closing probability: {result.get('closing_probability', 0)}%")
    print(f"Sentiment score: {result.get('sentiment_score', 'unknown')}")
    print(f"Urgency score: {result.get('urgency_score', 'unknown')}")
    print(f"Predicted response rate: {result.get('predicted_response_rate', 'unknown')}")
    print(f"ICP score: {result.get('icp_score', 'unknown')}")
    print(f"Strongest alignment: {result.get('company_alignment', {}).get('strongest_alignment', 'none')}")
    print(f"Emails generated: {len(result.get('email_drafts', []))}")
    print(f"HubSpot contact ID: {result.get('hubspot_contact_id', 'none')}")
    print(f"Errors: {result.get('errors', [])}")

    drafts = result.get("email_drafts", [])
    if len(drafts) >= 3:
        print(f"\n--- MESSAGE 1 APPRECIATION ---")
        print(f"Subject: {drafts[0].get('subject', '')}")
        print(f"Body: {drafts[0].get('body', '')}")
        print(f"\n--- MESSAGE 2 AUTHORITY ---")
        print(f"Subject: {drafts[1].get('subject', '')}")
        print(f"Body: {drafts[1].get('body', '')}")
        print(f"\n--- MESSAGE 3 VALUE ---")
        print(f"Subject: {drafts[2].get('subject', '')}")
        print(f"Body: {drafts[2].get('body', '')}")

if __name__ == "__main__":
    test_full_pipeline()