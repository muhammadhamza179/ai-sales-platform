import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from evals.evaluators import (
    evaluator_persona_accuracy,
    evaluator_icp_accuracy,
    evaluator_hallucination_check
)

print("\n=== TESTING EVALUATORS INDEPENDENTLY ===\n")

print("--- PERSONA ACCURACY EVALUATOR ---")

result = evaluator_persona_accuracy("VP Engineering", "VP Engineering")
print(f"Exact match: {result}")

result = evaluator_persona_accuracy("Head of Engineering", "VP Engineering")
print(f"Similar title: {result}")

result = evaluator_persona_accuracy("Marketing Manager", "VP Engineering")
print(f"Wrong title: {result}")

result = evaluator_persona_accuracy("Chief Technology Officer", "VP Engineering")
print(f"CTO vs VP Engineering: {result}")

print("\n--- ICP ACCURACY EVALUATOR ---")

result = evaluator_icp_accuracy("high", "high")
print(f"Exact match high: {result}")

result = evaluator_icp_accuracy("medium", "high")
print(f"Adjacent tier: {result}")

result = evaluator_icp_accuracy("low", "high")
print(f"Wrong tier: {result}")

print("\n--- HALLUCINATION CHECKER ---")

clean_email = "I noticed your team is growing fast and focused on developer tools."
research = "The company is growing and focuses on developer productivity"
result = evaluator_hallucination_check(clean_email, research, "TestCo")
print(f"Clean email: {result}")

hallucinated_email = "Congrats on raising $50M in Series B funding last month."
research = "The company raised seed funding last year"
result = evaluator_hallucination_check(hallucinated_email, research, "TestCo")
print(f"Hallucinated email: {result}")

verified_email = "Your Series A funding shows strong investor confidence."
research = "The company completed a series a funding round"
result = evaluator_hallucination_check(verified_email, research, "TestCo")
print(f"Verified claim: {result}")

print("\n=== ALL EVALUATOR TESTS COMPLETE ===")