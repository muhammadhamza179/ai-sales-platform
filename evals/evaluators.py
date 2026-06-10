import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import json
import time
import uuid
from agent.graph import create_graph

graph = create_graph()

def run_single_eval(company_name: str, linkedin_url: str) -> dict:
    initial_state = {
        "company_name": company_name,
        "linkedin_url": linkedin_url,
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
    start = time.time()
    result = graph.invoke(initial_state)
    elapsed = round(time.time() - start, 2)
    return {
        "time_seconds": elapsed,
        "predicted_persona": result.get("persona", {}).get("job_title", "unknown"),
        "predicted_icp": result.get("icp_score", "unknown"),
        "closing_probability": result.get("closing_probability", 0),
        "sentiment": result.get("sentiment_score", "unknown"),
        "industry": result.get("research_data", {}).get("industry", "unknown"),
        "funding_stage": result.get("research_data", {}).get("funding_stage", "unknown"),
        "sources_count": result.get("research_data", {}).get("sources_count", 0),
        "email_1_subject": result.get("email_drafts", [{}])[0].get("subject", "") if result.get("email_drafts") else "",
        "email_1_body": result.get("email_drafts", [{}])[0].get("body", "") if result.get("email_drafts") else "",
        "errors": result.get("errors", [])
    }

def score_persona_accuracy(predicted: str, expected: str) -> bool:
    predicted_lower = predicted.lower()
    expected_lower = expected.lower()
    keywords = expected_lower.split()
    matches = sum(1 for keyword in keywords if keyword in predicted_lower)
    return matches >= len(keywords) * 0.5

def score_icp_accuracy(predicted: str, expected: str) -> bool:
    return predicted.lower() == expected.lower()

def score_hallucination(email_body: str, research_summary: str) -> str:
    suspicious_patterns = [
        "raised $", "acquired by", "launched", "announced", "partnership with",
        "revenue of", "employees", "founded in", "headquartered in"
    ]
    found_claims = [p for p in suspicious_patterns if p.lower() in email_body.lower()]
    if not found_claims:
        return "clean"
    verified = [c for c in found_claims if c.lower() in research_summary.lower()]
    if len(verified) == len(found_claims):
        return "verified"
    return f"potential_hallucination: {[c for c in found_claims if c not in verified]}"

def run_full_eval(dataset_path: str = "evals/dataset.json"):
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    companies = dataset.get("companies", [])
    if not companies:
        print("No companies in dataset yet. Add companies first.")
        return

    results = []
    persona_correct = 0
    icp_correct = 0
    hallucination_clean = 0
    total_time = 0

    print(f"\n=== RUNNING EVALS ON {len(companies)} COMPANIES ===\n")

    for i, company in enumerate(companies):
        print(f"[{i+1}/{len(companies)}] Evaluating {company['company_name']}...")

        try:
            result = run_single_eval(company["company_name"], company.get("linkedin_url", ""))

            persona_match = score_persona_accuracy(
                result["predicted_persona"],
                company.get("expected_persona", "")
            )
            icp_match = score_icp_accuracy(
                result["predicted_icp"],
                company.get("expected_icp", "")
            )
            hallucination = score_hallucination(
                result["email_1_body"],
                company.get("research_summary_hint", "")
            )

            if persona_match:
                persona_correct += 1
            if icp_match:
                icp_correct += 1
            if hallucination == "clean" or hallucination == "verified":
                hallucination_clean += 1

            total_time += result["time_seconds"]

            eval_result = {
                "company": company["company_name"],
                "predicted_persona": result["predicted_persona"],
                "expected_persona": company.get("expected_persona", ""),
                "persona_correct": persona_match,
                "predicted_icp": result["predicted_icp"],
                "expected_icp": company.get("expected_icp", ""),
                "icp_correct": icp_match,
                "hallucination_check": hallucination,
                "closing_probability": result["closing_probability"],
                "time_seconds": result["time_seconds"],
                "email_1_subject": result["email_1_subject"],
                "errors": result["errors"]
            }
            results.append(eval_result)

            status = "PASS" if (persona_match and icp_match) else "FAIL"
            print(f"  Persona: {result['predicted_persona']} (expected: {company.get('expected_persona', '')}) — {'✓' if persona_match else '✗'}")
            print(f"  ICP: {result['predicted_icp']} (expected: {company.get('expected_icp', '')}) — {'✓' if icp_match else '✗'}")
            print(f"  Hallucination: {hallucination}")
            print(f"  Time: {result['time_seconds']}s | Status: {status}\n")

            time.sleep(3)

        except Exception as e:
            print(f"  ERROR: {str(e)}\n")

    total = len(companies)
    print("\n=== EVAL SUMMARY ===\n")
    print(f"Companies evaluated: {total}")
    print(f"Persona accuracy: {persona_correct}/{total} ({round(persona_correct/total*100)}%)")
    print(f"ICP accuracy: {icp_correct}/{total} ({round(icp_correct/total*100)}%)")
    print(f"Hallucination clean rate: {hallucination_clean}/{total} ({round(hallucination_clean/total*100)}%)")
    print(f"Average pipeline time: {round(total_time/total, 2)}s")

    output_path = "evals/eval_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "summary": {
                "total_companies": total,
                "persona_accuracy_percent": round(persona_correct/total*100),
                "icp_accuracy_percent": round(icp_correct/total*100),
                "hallucination_clean_percent": round(hallucination_clean/total*100),
                "average_time_seconds": round(total_time/total, 2)
            },
            "results": results
        }, f, indent=2)

    print(f"\nFull results saved to {output_path}")
    return results

if __name__ == "__main__":
    run_full_eval()