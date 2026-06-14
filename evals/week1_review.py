import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import json
import time
import uuid
import statistics
from agent.graph import create_graph

graph = create_graph()

TEST_COMPANIES = [
    {"name": "Notion", "url": "https://linkedin.com/company/notionhq"},
    {"name": "Linear", "url": "https://linkedin.com/company/linear-app"},
    {"name": "Loom", "url": "https://linkedin.com/company/loom-inc"},
    {"name": "Retool", "url": "https://linkedin.com/company/tryretool"},
    {"name": "Deel", "url": "https://linkedin.com/company/deel-hq"},
    {"name": "Webflow", "url": "https://linkedin.com/company/webflow-inc"},
    {"name": "Airtable", "url": "https://linkedin.com/company/airtable"},
    {"name": "Zapier", "url": "https://linkedin.com/company/zapier"},
    {"name": "Intercom", "url": "https://linkedin.com/company/intercom"},
    {"name": "Rippling", "url": "https://linkedin.com/company/rippling"},
    {"name": "Monday.com", "url": "https://linkedin.com/company/mondaydotcom"},
    {"name": "Calendly", "url": "https://linkedin.com/company/calendly"},
    {"name": "Vercel", "url": "https://linkedin.com/company/vercel"},
    {"name": "Stripe", "url": "https://linkedin.com/company/stripe"},
    {"name": "Figma", "url": "https://linkedin.com/company/figma"},
    {"name": "Brex", "url": "https://linkedin.com/company/brex-hq"},
    {"name": "Amplitude", "url": "https://linkedin.com/company/amplitude-analytics"},
    {"name": "Mixpanel", "url": "https://linkedin.com/company/mixpanel-inc"},
    {"name": "Asana", "url": "https://linkedin.com/company/asana"},
    {"name": "Hubspot", "url": "https://linkedin.com/company/hubspot"},
]

def run_company(company_name, linkedin_url):
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
    try:
        result = graph.invoke(initial_state)
        elapsed = round(time.time() - start, 2)
        return {
            "company": company_name,
            "success": True,
            "time_seconds": elapsed,
            "persona": result.get("persona", {}).get("job_title", "unknown"),
            "icp_score": result.get("icp_score", "unknown"),
            "closing_probability": result.get("closing_probability", 0),
            "sentiment": result.get("sentiment_score", "unknown"),
            "urgency": result.get("urgency_score", "unknown"),
            "industry": result.get("research_data", {}).get("industry", "unknown"),
            "funding_stage": result.get("research_data", {}).get("funding_stage", "unknown"),
            "sources_found": result.get("research_data", {}).get("sources_count", 0),
            "emails_generated": len(result.get("email_drafts", [])),
            "hubspot_created": result.get("hubspot_contact_id") is not None,
            "errors": result.get("errors", []),
            "error_count": len(result.get("errors", []))
        }
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        return {
            "company": company_name,
            "success": False,
            "time_seconds": elapsed,
            "error": str(e),
            "errors": [str(e)],
            "error_count": 1,
            "emails_generated": 0,
            "hubspot_created": False,
            "sources_found": 0
        }

def run_week1_review():
    print("\n" + "="*60)
    print("WEEK 1 REVIEW — RUNNING 20 COMPANIES")
    print("="*60 + "\n")

    results = []
    start_time = time.time()

    for i, company in enumerate(TEST_COMPANIES):
        print(f"[{i+1}/20] Running {company['name']}...")
        result = run_company(company["name"], company["url"])

        status = "SUCCESS" if result["success"] else "FAILED"
        if result["success"]:
            print(f"  Time: {result['time_seconds']}s | ICP: {result['icp_score']} | Closing: {result.get('closing_probability', 0)}% | Emails: {result['emails_generated']} | [{status}]")
        else:
            print(f"  Time: {result['time_seconds']}s | Error: {result.get('error', 'unknown')[:60]} | [{status}]")

        results.append(result)
        time.sleep(3)

    total_time = round(time.time() - start_time, 2)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    times = [r["time_seconds"] for r in successful]
    sorted_times = sorted(times)

    p50 = statistics.median(times) if times else 0
    p95 = sorted_times[int(len(sorted_times) * 0.95) - 1] if len(sorted_times) >= 2 else (sorted_times[-1] if sorted_times else 0)
    avg_time = round(statistics.mean(times), 2) if times else 0

    hubspot_success = sum(1 for r in successful if r.get("hubspot_created"))
    total_emails = sum(r.get("emails_generated", 0) for r in successful)
    total_sources = sum(r.get("sources_found", 0) for r in successful)
    avg_closing_prob = round(statistics.mean([r.get("closing_probability", 0) for r in successful]), 1) if successful else 0

    icp_distribution = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    for r in successful:
        icp = r.get("icp_score", "unknown").lower()
        if icp in icp_distribution:
            icp_distribution[icp] += 1
        else:
            icp_distribution["unknown"] += 1

    print("\n" + "="*60)
    print("WEEK 1 PERFORMANCE SUMMARY")
    print("="*60)
    print(f"\nOVERALL PERFORMANCE")
    print(f"  Total companies run:      20")
    print(f"  Successful runs:          {len(successful)}/20 ({round(len(successful)/20*100)}%)")
    print(f"  Failed runs:              {len(failed)}/20")
    print(f"  Total wall clock time:    {total_time}s")
    print(f"\nLATENCY METRICS")
    print(f"  P50 latency:              {round(p50, 2)}s")
    print(f"  P95 latency:              {round(p95, 2)}s")
    print(f"  Average latency:          {avg_time}s")
    print(f"  Fastest run:              {min(times) if times else 0}s")
    print(f"  Slowest run:              {max(times) if times else 0}s")
    print(f"\nOUTPUT QUALITY")
    print(f"  Total emails generated:   {total_emails}")
    print(f"  Avg emails per run:       {round(total_emails/len(successful), 1) if successful else 0}")
    print(f"  Total sources found:      {total_sources}")
    print(f"  Avg sources per run:      {round(total_sources/len(successful), 1) if successful else 0}")
    print(f"  HubSpot success rate:     {hubspot_success}/{len(successful)} ({round(hubspot_success/len(successful)*100) if successful else 0}%)")
    print(f"\nSCORING METRICS")
    print(f"  Avg closing probability:  {avg_closing_prob}%")
    print(f"  ICP distribution:         High {icp_distribution['high']} | Medium {icp_distribution['medium']} | Low {icp_distribution['low']}")
    print(f"\nFAILED RUNS")
    if failed:
        for r in failed:
            print(f"  {r['company']}: {r.get('error', 'unknown error')[:80]}")
    else:
        print(f"  None. All runs completed successfully.")

    summary = {
        "week": 1,
        "date": time.strftime("%Y-%m-%d"),
        "total_companies": 20,
        "successful_runs": len(successful),
        "failed_runs": len(failed),
        "success_rate_percent": round(len(successful)/20*100),
        "p50_latency_seconds": round(p50, 2),
        "p95_latency_seconds": round(p95, 2),
        "average_latency_seconds": avg_time,
        "total_emails_generated": total_emails,
        "hubspot_success_rate_percent": round(hubspot_success/len(successful)*100) if successful else 0,
        "average_closing_probability": avg_closing_prob,
        "icp_distribution": icp_distribution,
        "total_wall_clock_seconds": total_time,
        "results": results
    }

    output_path = "evals/week1_results.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nFull results saved to {output_path}")
    print("="*60)
    return summary

if __name__ == "__main__":
    run_week1_review()