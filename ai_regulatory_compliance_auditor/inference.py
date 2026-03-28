#!/usr/bin/env python3
"""
AI Regulatory Compliance Auditor - Inference Script.
Uses OpenAI client to run compliance auditing tasks.
"""

import os
import json
import sys
from openai import OpenAI

from compliance_env.env import (
    ComplianceAuditorEnvironment,
    Action,
    ComplianceFinding,
    ViolationType,
    SeverityLevel
)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))


def create_client() -> OpenAI:
    """Create OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY", "") or os.getenv("HF_TOKEN", "")
    return OpenAI(api_key=api_key, base_url=API_BASE_URL, timeout=30)


def create_system_prompt() -> str:
    """Create system prompt for compliance auditor."""
    return """You are an expert AI Regulatory Compliance Auditor. Review policy documents and identify regulatory compliance violations.

Expertise: GDPR, CCPA, ePrivacy Directive.

For each violation provide:
- violation_type: Category
- severity: critical|high|medium|low
- location: Where in document
- description: Explanation
- evidence: Direct quote
- regulatory_reference: (optional)

Violation Types:
- missing_mandatory_clause, data_retention_violation, consent_requirement_violation
- cross_border_transfer_violation, data_subject_rights_violation, purpose_limitation_violation
- data_minimization_violation, security_measures_violation, breach_notification_violation
- third_party_sharing_violation, children_data_violation, automated_decision_violation
- document_contradiction, regulatory_mismatch

Respond with JSON."""


def create_user_prompt(obs) -> str:
    """Create user prompt from observation."""
    return f"""TASK: {obs.task_description}

DOCUMENT:
{obs.document_text}

Submit JSON:
{{"reasoning": "analysis", "findings": [{{"violation_type": "...", "severity": "...", "location": "...", "description": "...", "evidence": "..."}}], "is_submission": true}}

Step: {obs.step_count + 1}/{obs.max_steps}"""


def parse_llm_response(text: str) -> dict:
    """Parse LLM response."""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except json.JSONDecodeError:
        pass
    return {"findings": [], "is_submission": True}


def convert_to_action(parsed: dict) -> Action:
    """Convert to Action."""
    findings = []
    for f in parsed.get("findings", []):
        try:
            try:
                vt = ViolationType(f.get("violation_type", "missing_mandatory_clause"))
            except ValueError:
                vt = ViolationType.MISSING_MANDATORY_CLAUSE
            try:
                sev = SeverityLevel(f.get("severity", "medium").lower())
            except ValueError:
                sev = SeverityLevel.MEDIUM
            findings.append(ComplianceFinding(
                violation_type=vt, severity=sev,
                location=f.get("location", "Unknown"),
                description=f.get("description", ""),
                evidence=f.get("evidence", ""),
                regulatory_reference=f.get("regulatory_reference")
            ))
        except Exception as e:
            print(f"Warning: {e}")
    return Action(findings=findings, is_submission=parsed.get("is_submission", True))


def run_task(client: OpenAI, env: ComplianceAuditorEnvironment, task_id: str) -> dict:
    """Run a single task."""
    print(f"\n{'='*60}")
    print(f"Task: {task_id.upper()}")
    print(f"{'='*60}")
    
    obs = env.reset(task_id)
    print(f"Description: {obs.task_description}")
    print(f"Max Steps: {obs.max_steps}")
    
    done = False
    steps = 0
    all_findings = []
    
    while not done:
        steps += 1
        print(f"\nStep {steps}/{obs.max_steps}")
        
        try:
            # Debug prints
            print(f"Base URL: {API_BASE_URL}")
            print(f"Model: {MODEL_NAME}")
            token = os.getenv("HF_TOKEN", "")
            print(f"Token starts with: {token[:5] if token else 'None'}")
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": create_system_prompt()},
                    {"role": "user", "content": create_user_prompt(obs)}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            text = response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            text = '{"findings": [], "is_submission": true}'
        
        parsed = parse_llm_response(text)
        action = convert_to_action(parsed)
        obs, reward, done, info = env.step(action)
        all_findings.extend(action.findings)
        
        print(f"Reward: {reward:.4f} | Correct: {info['reward_breakdown']['correct_findings']} | FP: {info['reward_breakdown']['false_positives']}")
    
    return {
        "task_id": task_id,
        "steps": steps,
        "final_score": obs.previous_rewards[-1] if obs.previous_rewards else 0,
        "findings_count": len(all_findings),
        "breakdown": info["reward_breakdown"]
    }


def main():
    """Main entry point."""
    print("="*60)
    print("AI REGULATORY COMPLIANCE AUDITOR")
    print("="*60)
    print(f"Model: {MODEL_NAME}")
    print(f"Temperature: {TEMPERATURE}")
    
    client = create_client()
    env = ComplianceAuditorEnvironment()
    
    results = []
    for task_id in ["easy", "medium", "hard"]:
        result = run_task(client, env, task_id)
        results.append(result)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("="*60)
    
    total = 0
    for r in results:
        print(f"\n{r['task_id'].upper()}: Score={r['final_score']:.4f} Findings={r['findings_count']}")
        total += r['final_score']
    
    avg = total / len(results) if results else 0
    print(f"\nAVERAGE SCORE: {avg:.4f}")
    
    with open("inference_results.json", "w") as f:
        json.dump({"model": MODEL_NAME, "tasks": results, "average_score": avg}, f, indent=2)
    
    print("Results saved to inference_results.json")
    return avg


if __name__ == "__main__":
    score = main()
    sys.exit(0 if score > 0 else 1)