import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


class HubSpotClient:
    def __init__(self):
        self.token = os.getenv("HUBSPOT_ACCESS_TOKEN")
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def create_contact(self, company_name: str, linkedin_url: str, icp_score: str, persona_title: str, closing_probability: int) -> str:
        url = f"{self.base_url}/crm/v3/objects/contacts"
        
        # Remove 'description' — it doesn't exist in HubSpot
        payload = {
            "properties": {
                "company": company_name,
                "website": linkedin_url,
                "jobtitle": persona_title,
                "hs_lead_status": "NEW"
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json().get("id", "unknown")

    def create_note(self, contact_id: str, content: str) -> str:
        url = f"{self.base_url}/crm/v3/objects/notes"
        payload = {
            "properties": {
                "hs_note_body": content,
                "hs_timestamp": str(int(time.time() * 1000))
            }
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        note_id = response.json().get("id", "unknown")
        assoc_url = f"{self.base_url}/crm/v3/objects/notes/{note_id}/associations/contacts/{contact_id}/note_to_contact"
        requests.put(assoc_url, headers=self.headers)
        return note_id