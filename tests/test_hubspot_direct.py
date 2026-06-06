import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HUBSPOT_ACCESS_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test 1: Try to create a simple contact with minimal fields
print("Test 1: Creating contact with minimal fields...")
payload_minimal = {
    "properties": {
        "company": "Test Company Minimal",
        "firstname": "Test",
        "lastname": "Contact"
    }
}

response = requests.post(
    "https://api.hubapi.com/crm/v3/objects/contacts",
    json=payload_minimal,
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Test 2: Try with your exact payload
print("Test 2: Creating contact with your payload...")
payload_full = {
    "properties": {
        "company": "Notion",
        "website": "https://linkedin.com/company/notionhq",
        "jobtitle": "Head of Product",
        "hs_lead_status": "NEW",
        "description": "ICP Score: high | Closing Probability: 70% | Added by AI Sales Platform"
    }
}

response2 = requests.post(
    "https://api.hubapi.com/crm/v3/objects/contacts",
    json=payload_full,
    headers=headers
)

print(f"Status: {response2.status_code}")
print(f"Response: {response2.text}")