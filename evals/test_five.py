import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import time
from evals.evaluators import run_single_eval, score_persona_accuracy, score_icp_accuracy

companies_to_test = [
    {"company_name": "Notion", "linkedin_url": "https://linkedin.com/company/notionhq", "expected_persona": "Head of Operations", "expected_icp": "high"},
    {"company_name": "Linear", "linkedin_url": "https://linkedin.com/company/linear-app", "expected_persona": "VP Engineering", "expected_icp": "high"},
    {"company_name": "Loom", "linkedin_url": "https://linkedin.com/company/loom-inc", "expected_persona": "Head of Sales", "expected_icp": "high"},
    {"company_name": "Retool", "linkedin_url": "https://linkedin.com/company/tryretool", "expected_persona": "VP Engineering", "expected_icp": "high"},
    {"company_name": "Deel", "linkedin_url": "https://linkedin.com/company/deel-hq", "expected_persona": "Head of HR", "expected_icp": "high"},
]

persona_correct = 0
icp_correct = 0

print("\n=== RUNNING 5 COMPANY EVAL TEST ===\n")

for company in companies_to_test:
    print(f"Testing {company['company_name']}...")
    try:
        result = run_single_eval(company["company_name"], company["linkedin_url"])
        persona_match = score_persona_accuracy(result["predicted_persona"], company["expected_persona"])
        icp_match = score_icp_accuracy(result["predicted_icp"], company["expected_icp"])
        if persona_match:
            persona_correct += 1
        if icp_match:
            icp_correct += 1
        print(f"  Predicted persona: {result['predicted_persona']}")
        print(f"  Expected persona: {company['expected_persona']}")
        print(f"  Persona match: {'YES' if persona_match else 'NO'}")
        print(f"  Predicted ICP: {result['predicted_icp']}")
        print(f"  Expected ICP: {company['expected_icp']}")
        print(f"  ICP match: {'YES' if icp_match else 'NO'}")
        print(f"  Time: {result['time_seconds']}s")
        print(f"  Email subject: {result['email_1_subject']}")
        print()
        time.sleep(3)
    except Exception as e:
        print(f"  ERROR: {str(e)}\n")

print(f"=== RESULTS ===")
print(f"Persona accuracy: {persona_correct}/5 ({persona_correct*20}%)")
print(f"ICP accuracy: {icp_correct}/5 ({icp_correct*20}%)")