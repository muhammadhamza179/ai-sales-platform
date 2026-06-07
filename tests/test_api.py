import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    print("\n=== TEST 1: Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("PASSED")


def test_analyze_prospect():
    print("\n=== TEST 2: Analyze Prospect ===")
    data = {
        "company_name": "Notion",
        "linkedin_url": "https://linkedin.com/company/notionhq"
    }
    print(f"Sending request for: {data['company_name']}")
    start = time.time()
    response = requests.post(f"{BASE_URL}/analyze", data=data)
    elapsed = round(time.time() - start, 2)
    print(f"Status: {response.status_code}")
    print(f"Time: {elapsed} seconds")
    if response.status_code == 200:
        result = response.json()
        print(f"Closing Probability: {result.get('closing_probability')}%")
        print(f"Sentiment: {result.get('sentiment_score')}")
        print(f"ICP Score: {result.get('icp_score')}")
        print(f"Emails Generated: {len(result.get('email_drafts', []))}")
        print(f"HubSpot ID: {result.get('hubspot_contact_id')}")
        print(f"Errors: {result.get('errors')}")
        if result.get("email_drafts"):
            print(f"\nMessage 1 Subject: {result['email_drafts'][0].get('subject', '')}")
            print(f"Message 1 Body: {result['email_drafts'][0].get('body', '')}")
        print("PASSED")
    else:
        print(f"FAILED: {response.text}")


def test_continue_conversation():
    print("\n=== TEST 3: Continue Conversation ===")
    data = {
        "company_name": "Notion",
        "prospect_reply": "Thanks for reaching out but we are not looking at new tools right now",
        "conversation_history": json.dumps([
            {"role": "us", "message": "Notion's 240% growth is impressive"},
            {"role": "them", "message": "Thanks for reaching out but we are not looking at new tools right now"}
        ]),
        "closing_probability": 70
    }
    response = requests.post(f"{BASE_URL}/continue-conversation", data=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Objection Type: {result.get('objection_type')}")
        print(f"Response: {result.get('response')}")
        print(f"Updated Probability: {result.get('closing_probability_update')}%")
        print(f"Next Action: {result.get('recommended_next_action')}")
        print("PASSED")
    else:
        print(f"FAILED: {response.text}")


if __name__ == "__main__":
    print("Make sure the server is running: uvicorn api.main:app --reload")
    print("Starting API tests...\n")
    test_health()
    test_analyze_prospect()
    test_continue_conversation()
    print("\n=== ALL TESTS COMPLETE ===")