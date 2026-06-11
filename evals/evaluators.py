import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import json
import time
import uuid
import re
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
        "pain_points": result.get("research_data", {}).get("pain_points", []),
        "email_1_subject": result.get("email_drafts", [{}])[0].get("subject", "") if result.get("email_drafts") else "",
        "email_1_body": result.get("email_drafts", [{}])[0].get("body", "") if result.get("email_drafts") else "",
        "email_2_body": result.get("email_drafts", [{}])[1].get("body", "") if result.get("email_drafts") and len(result.get("email_drafts", [])) > 1 else "",
        "email_3_body": result.get("email_drafts", [{}])[2].get("body", "") if result.get("email_drafts") and len(result.get("email_drafts", [])) > 2 else "",
        "research_raw_text": " ".join([
            result.get("research_data", {}).get("summary", ""),
            " ".join(result.get("research_data", {}).get("recent_news", [])),
            " ".join(result.get("research_data", {}).get("growth_signals", [])),
        ]),
        "errors": result.get("errors", [])
    }


# EVALUATOR 1 — PERSONA ACCURACY
def evaluator_persona_accuracy(predicted_persona: str, expected_persona: str) -> dict:
    predicted_lower = predicted_persona.lower().strip()
    expected_lower = expected_persona.lower().strip()

    if predicted_lower == expected_lower:
        return {"correct": True, "score": 1.0, "reason": "exact match"}

    expected_words = [w for w in expected_lower.split() if len(w) > 2]
    predicted_words = predicted_lower.split()
    matches = sum(1 for word in expected_words if word in predicted_words)
    match_ratio = matches / len(expected_words) if expected_words else 0

    if match_ratio >= 0.6:
        return {"correct": True, "score": match_ratio, "reason": f"partial match {matches}/{len(expected_words)} keywords"}

    seniority_map = {
        "vp": ["vice president", "vp of", "head of"],
        "head": ["director", "lead", "chief"],
        "director": ["head of", "vp", "senior manager"],
        "cto": ["vp engineering", "head of engineering", "chief technology"],
        "cfo": ["vp finance", "head of finance", "chief financial"],
        "ceo": ["founder", "co-founder", "president"]
    }
    for key, synonyms in seniority_map.items():
        if key in expected_lower:
            for synonym in synonyms:
                if synonym in predicted_lower:
                    return {"correct": True, "score": 0.7, "reason": f"synonym match: {synonym}"}

    return {"correct": False, "score": 0.0, "reason": f"no match: predicted '{predicted_persona}' vs expected '{expected_persona}'"}


# EVALUATOR 2 — ICP ACCURACY
def evaluator_icp_accuracy(predicted_icp: str, expected_icp: str) -> dict:
    predicted_lower = predicted_icp.lower().strip()
    expected_lower = expected_icp.lower().strip()

    if predicted_lower == expected_lower:
        return {"correct": True, "score": 1.0, "reason": "exact match"}

    adjacency = {
        "high": ["medium"],
        "medium": ["high", "low"],
        "low": ["medium"]
    }
    if predicted_lower in adjacency.get(expected_lower, []):
        return {"correct": False, "score": 0.5, "reason": f"adjacent tier: predicted {predicted_lower} vs expected {expected_lower}"}

    return {"correct": False, "score": 0.0, "reason": f"wrong tier: predicted {predicted_lower} vs expected {expected_lower}"}


# EVALUATOR 3 — HALLUCINATION CHECKER
def evaluator_hallucination_check(email_body: str, research_raw_text: str, company_name: str) -> dict:
    if not email_body:
        return {"hallucination_detected": False, "score": 1.0, "reason": "no email to check", "flagged_claims": []}

    claim_patterns = [
        r'\$[\d,]+\s*(million|billion|M|B)',
        r'raised\s+[\$\d]',
        r'revenue\s+of\s+[\$\d]',
        r'[\d,]+\s*employees',
        r'founded\s+in\s+\d{4}',
        r'acquired\s+by\s+\w+',
        r'series\s+[a-eA-E]\s+funding',
        r'valued\s+at\s+[\$\d]',
        r'partnership\s+with\s+\w+',
        r'launched\s+\w+\s+in\s+\d{4}',
    ]

    flagged_claims = []
    for pattern in claim_patterns:
        matches = re.findall(pattern, email_body, re.IGNORECASE)
        for match in matches:
            match_str = match if isinstance(match, str) else " ".join(match)
            if match_str.lower() not in research_raw_text.lower():
                flagged_claims.append(match_str)

    if not flagged_claims:
        return {
            "hallucination_detected": False,
            "score": 1.0,
            "reason": "no suspicious claims found",
            "flagged_claims": []
        }

    verified = [c for c in flagged_claims if c.lower() in research_raw_text.lower()]
    unverified = [c for c in flagged_claims if c.lower() not in research_raw_text.lower()]

    if unverified:
        return {
            "hallucination_detected": True,
            "score": 0.0,
            "reason": f"found {len(unverified)} unverified claims",
            "flagged_claims": unverified
        }

    return {
        "hallucination_detected": False,
        "score": 1.0,
        "reason": f"all {len(verified)} claims verified in research",
        "flagged_claims": []
    }


# MAIN EVAL RUNNER
def run_full_eval(dataset_path: str = "evals/dataset.json", max_companies: int = None):
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    companies = dataset.get("companies", [])
    if max_companies:
        companies = companies[:max_companies]

    if not companies:
        print("No companies in dataset. Add companies first.")
        return

    results = []
    persona_scores = []
    icp_scores = []
    hallucination_scores = []
    times = []

    print(f"\n=== RUNNING FULL EVAL ON {len(companies)} COMPANIES ===\n")

    for i, company in enumerate(companies):
        print(f"[{i+1}/{len(companies)}] {company['company_name']}...")

        try:
            result = run_single_eval(
                company["company_name"],
                company.get("linkedin_url", "")
            )

            persona_eval = evaluator_persona_accuracy(
                result["predicted_persona"],
                company.get("expected_persona", "")
            )

            icp_eval = evaluator_icp_accuracy(
                result["predicted_icp"],
                company.get("expected_icp", "")
            )

            hallucination_eval = evaluator_hallucination_check(
                result["email_1_body"],
                result["research_raw_text"],
                company["company_name"]
            )

            persona_scores.append(1 if persona_eval["correct"] else 0)
            icp_scores.append(1 if icp_eval["correct"] else 0)
            hallucination_scores.append(1 if not hallucination_eval["hallucination_detected"] else 0)
            times.append(result["time_seconds"])

            eval_result = {
                "company": company["company_name"],
                "predicted_persona": result["predicted_persona"],
                "expected_persona": company.get("expected_persona", ""),
                "persona_eval": persona_eval,
                "predicted_icp": result["predicted_icp"],
                "expected_icp": company.get("expected_icp", ""),
                "icp_eval": icp_eval,
                "hallucination_eval": hallucination_eval,
                "closing_probability": result["closing_probability"],
                "time_seconds": result["time_seconds"],
                "email_1_subject": result["email_1_subject"],
                "email_1_body": result["email_1_body"][:200],
                "errors": result["errors"]
            }
            results.append(eval_result)

            persona_status = "PASS" if persona_eval["correct"] else "FAIL"
            icp_status = "PASS" if icp_eval["correct"] else "FAIL"
            hall_status = "CLEAN" if not hallucination_eval["hallucination_detected"] else "FLAGGED"

            print(f"  Persona: {result['predicted_persona']} [{persona_status}] — {persona_eval['reason']}")
            print(f"  ICP: {result['predicted_icp']} [{icp_status}] — {icp_eval['reason']}")
            print(f"  Hallucination: [{hall_status}] — {hallucination_eval['reason']}")
            print(f"  Closing: {result['closing_probability']}% | Time: {result['time_seconds']}s\n")

            time.sleep(4)

        except Exception as e:
            print(f"  ERROR: {str(e)}\n")
            time.sleep(2)

    total = len(results)
    if total == 0:
        print("No results. Check your API keys.")
        return

    persona_accuracy = round(sum(persona_scores) / total * 100)
    icp_accuracy = round(sum(icp_scores) / total * 100)
    hallucination_clean_rate = round(sum(hallucination_scores) / total * 100)
    avg_time = round(sum(times) / total, 2)
    sorted_times = sorted(times)
    p95_index = max(0, int(total * 0.95) - 1)
    p95_time = sorted_times[p95_index]

    print("\n" + "="*50)
    print("EVAL SUMMARY")
    print("="*50)
    print(f"Companies evaluated:      {total}")
    print(f"Persona accuracy:         {sum(persona_scores)}/{total} ({persona_accuracy}%)")
    print(f"ICP accuracy:             {sum(icp_scores)}/{total} ({icp_accuracy}%)")
    print(f"Hallucination clean rate: {sum(hallucination_scores)}/{total} ({hallucination_clean_rate}%)")
    print(f"Average pipeline time:    {avg_time}s")
    print(f"P95 latency:              {p95_time}s")
    print("="*50)

    summary = {
        "eval_date": time.strftime("%Y-%m-%d"),
        "total_companies": total,
        "persona_accuracy_percent": persona_accuracy,
        "icp_accuracy_percent": icp_accuracy,
        "hallucination_clean_rate_percent": hallucination_clean_rate,
        "average_time_seconds": avg_time,
        "p95_latency_seconds": p95_time,
        "persona_correct": sum(persona_scores),
        "icp_correct": sum(icp_scores),
        "hallucination_clean": sum(hallucination_scores),
        "results": results
    }

    output_path = "evals/eval_results.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nFull results saved to {output_path}")
    return summary


if __name__ == "__main__":
    max_companies = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_full_eval(max_companies=max_companies)