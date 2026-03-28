# AI Regulatory Compliance Auditor

A production-ready **OpenEnv** environment that simulates corporate data privacy and regulatory compliance auditing workflows. Agents act as compliance auditors reviewing policy documents to identify regulatory violations.

![OpenEnv Compatible](https://img.shields.io/badge/OpenEnv-Compatible-brightgreen)
![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Environment Specification](#environment-specification)
- [Task Descriptions](#task-descriptions)
- [Reward Design](#reward-design)
- [Installation](#installation)
- [Usage](#usage)
- [Docker Deployment](#docker-deployment)
- [Hugging Face Deployment](#hugging-face-deployment)
- [Example Output](#example-output)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

The AI Regulatory Compliance Auditor is an OpenEnv-compliant environment designed to test and evaluate AI agents on their ability to:

1. **Analyze regulatory documents** for compliance violations
2. **Identify missing mandatory clauses** required by GDPR, CCPA, and other regulations
3. **Detect contradictions** between document sections
4. **Cross-reference multiple documents** to find interdependent compliance issues
5. **Classify violation severity** appropriately

This environment simulates real-world compliance auditing tasks that data protection officers, legal teams, and compliance auditors perform regularly.

## Features

- **Three Difficulty Levels**: Easy, Medium, and Hard tasks with increasing complexity
- **Realistic Documents**: Privacy policies, data processing agreements, cookie policies, and retention policies
- **Deterministic Grading**: Reproducible scoring with no randomness
- **Partial Credit**: Rewards for partially correct findings
- **False Positive Penalties**: Discourages hallucinated violations
- **Structured Actions**: Pydantic-validated findings with violation types and severity levels
- **OpenEnv Compliant**: Full implementation of the OpenEnv specification

## Environment Specification

### Observation Space

| Field | Type | Description |
|-------|------|-------------|
| `document_text` | `str` | The regulatory document text to audit |
| `step_count` | `int` | Current step number in the episode |
| `max_steps` | `int` | Maximum steps allowed for this episode |
| `task_id` | `str` | Task identifier: `easy`, `medium`, or `hard` |
| `task_description` | `str` | Description of the auditing task |
| `previous_findings` | `List[ComplianceFinding]` | Findings submitted in previous steps |
| `previous_rewards` | `List[float]` | Rewards received in previous steps |
| `is_final` | `bool` | Whether this is the final step |

### Action Space

| Field | Type | Description |
|-------|------|-------------|
| `findings` | `List[ComplianceFinding]` | List of compliance findings identified |
| `is_submission` | `bool` | Whether this is a final submission |
| `reasoning` | `Optional[str]` | Optional reasoning behind findings |

### ComplianceFinding Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `violation_type` | `ViolationType` | Yes | Category of violation |
| `severity` | `SeverityLevel` | Yes | Severity level (critical, high, medium, low) |
| `location` | `str` | Yes | Where in document the violation was found |
| `description` | `str` | Yes | Clear description of the violation |
| `evidence` | `str` | Yes | Direct quote from the document |
| `regulatory_reference` | `Optional[str]` | No | Reference to specific regulation |

### Violation Types

- `missing_mandatory_clause` - Required clauses or disclosures are missing
- `data_retention_violation` - Issues with data retention periods
- `consent_requirement_violation` - Problems with consent mechanisms
- `cross_border_transfer_violation` - Issues with international data transfers
- `data_subject_rights_violation` - Problems with data subject rights
- `purpose_limitation_violation` - Data used beyond stated purposes
- `data_minimization_violation` - Collecting more data than necessary
- `security_measures_violation` - Inadequate security measures
- `breach_notification_violation` - Issues with breach notification procedures
- `third_party_sharing_violation` - Problems with third-party data sharing
- `children_data_violation` - Issues with children's data protection
- `automated_decision_violation` - Problems with automated decision-making
- `document_contradiction` - Contradictions within or between documents
- `regulatory_mismatch` - Inconsistencies with regulatory requirements

## Task Descriptions

### Task 1: Easy (Missing Mandatory Clause)

**Document**: TechFlow Solutions Inc. Privacy Policy

**Objective**: Identify missing mandatory GDPR clauses in a privacy policy.

**Ground Truth Violations** (2 violations):
1. Missing right to lodge a complaint with supervisory authority (GDPR Article 77)
2. Missing Data Protection Officer (DPO) contact information (GDPR Articles 37-39)

**Max Steps**: 5

**Difficulty**: Single document, obvious omissions

---

### Task 2: Medium (Contradictory Consent Requirements)

**Document**: DataStream Analytics Corp. Data Privacy Framework

**Objective**: Detect contradictions between consent requirement sections.

**Ground Truth Violations** (4 violations):
1. Direct contradiction: Section A.4 requires opt-in, but Section B.1 auto-enrolls on account creation
2. Third-party sharing: Section A.2 requires explicit consent, but Section B.2 allows automatic sharing
3. Behavioral advertising: Section B.3 uses terms of service acceptance instead of explicit consent
4. Telemarketing: Section B.4 allows phone contact without additional consent

**Max Steps**: 8

**Difficulty**: Requires multi-clause reasoning to identify contradictions

---

### Task 3: Hard (Multi-Document Cross-Reference)

**Documents**: CloudSync Technologies Inc.
- Data Processing Agreement (DPA)
- Cookie Policy
- Data Retention Policy

**Objective**: Perform comprehensive multi-document audit identifying individual violations and cross-document inconsistencies.

**Ground Truth Violations** (10 violations):
1. Incomplete breach notification requirements (DPA)
2. Missing sub-processor list (DPA)
3. Transfer to Brazil without legal basis (DPA)
4. Advertising cookies without explicit consent (Cookie Policy)
5. Insufficient third-party cookie disclosure (Cookie Policy)
6. Excessive account data retention (Retention Policy)
7. Missing cookie data retention periods (Retention Policy)
8. Sub-processor disclosure inconsistency (Cross-document)
9. Termination vs retention conflict (Cross-document)
10. Cookie consent vs DPA instructions conflict (Cross-document)

**Max Steps**: 15

**Difficulty**: Requires reading multiple documents, cross-referencing, and detecting subtle interdependencies

## Reward Design

### Scoring Formula

```
Final Score = (Correct Findings × 1.0) + (Severity Bonus × 0.25) - (False Positives × 0.5) - (Repetitions × 0.1)
Normalized Score = max(0, min(1, Final Score / Max Possible Score))
```

### Reward Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Correct Finding | +1.0 | Finding matches ground truth (violation type + location) |
| Severity Bonus | +0.25 | Severity classification matches exactly |
| False Positive | -0.5 | Finding does not match any ground truth violation |
| Repetition | -0.1 | Identical finding submitted multiple times |

### Match Threshold

Findings are matched to ground truth using a similarity threshold of 0.6, considering:
- Violation type match (40% weight)
- Location similarity (30% weight)
- Description/evidence similarity (30% weight)

### Severity Scoring

| Agent Severity | Ground Truth | Score |
|----------------|--------------|-------|
| Exact match | Exact match | 1.0 |
| ±1 level | - | 0.5 |
| ±2 levels | - | 0.25 |
| ±3 levels | - | 0.0 |

## Installation

### Prerequisites

- Python 3.9+
- pip or conda
- OpenAI API key (for inference)

### Local Installation

```bash
# Clone or navigate to the project directory
cd ai_regulatory_compliance_auditor

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Set the following environment variables before running inference:

```bash
export OPENAI_API_KEY="your-api-key-here"
export API_BASE_URL="https://api.openai.com/v1"  # Optional, default shown
export MODEL_NAME="gpt-4"                        # Optional, default shown
export TEMPERATURE="0"                           # Optional, for deterministic output
export MAX_TOKENS="4000"                         # Optional, default shown
```

## Usage

### Using the Environment in Python

```python
from src.environment import ComplianceAuditorEnvironment
from src.models import Action, ComplianceFinding, ViolationType, SeverityLevel

# Create environment
env = ComplianceAuditorEnvironment()

# Reset for a specific task
observation = env.reset("easy")

print(f"Task: {observation.task_description}")
print(f"Document length: {len(observation.document_text)} characters")

# Create a finding
finding = ComplianceFinding(
    violation_type=ViolationType.MISSING_MANDATORY_CLAUSE,
    severity=SeverityLevel.HIGH,
    location="Section 9: YOUR RIGHTS",
    description="Missing right to lodge complaint with supervisory authority",
    evidence="Section 9 lists rights but omits complaint right",
    regulatory_reference="GDPR Article 77"
)

# Submit action
action = Action(
    findings=[finding],
    is_submission=True
)

# Step environment
observation, reward, done, info = env.step(action)

print(f"Reward: {reward}")
print(f"Done: {done}")
print(f"Info: {info}")

# Get full state
state = env.state()
```

### Running Inference

```bash
# Set your API key
export OPENAI_API_KEY="sk-..."

# Run all tasks
python inference.py
```

The script will:
1. Initialize the OpenAI client
2. Run all three tasks sequentially
3. Print detailed results for each task
4. Save results to `inference_results.json`
5. Display average score

## Docker Deployment

### Building the Docker Image

```bash
cd ai_regulatory_compliance_auditor
docker build -t compliance-auditor .
```

### Running the Container

```bash
# Run with environment variables
docker run \
  -e OPENAI_API_KEY="sk-..." \
  -e MODEL_NAME="gpt-4" \
  compliance-auditor
```

### Docker Compose (Optional)

```yaml
version: '3.8'
services:
  compliance-auditor:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL_NAME=gpt-4
      - TEMPERATURE=0
    volumes:
      - ./results:/app/results
```

## Hugging Face Deployment

### Creating a Hugging Face Space

1. **Create a new Space** on [Hugging Face](https://huggingface.co/new-space)
2. Select **Docker** as the SDK
3. Choose **Blank** template

### Upload Files

Upload the following files to your Space:

```
your-space/
├── Dockerfile
├── requirements.txt
├── openenv.yaml
├── inference.py
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── documents.py
│   ├── tasks.py
│   ├── graders.py
│   └── environment.py
└── README.md
```

### Configure Secrets

In your Space settings, add the following secrets:

- `OPENAI_API_KEY`: Your OpenAI API key
- `HF_TOKEN`: (Optional) Hugging Face token for private models

### Environment Variables

Set in Space settings:

```
MODEL_NAME=gpt-4
API_BASE_URL=https://api.openai.com/v1
TEMPERATURE=0
MAX_TOKENS=4000
```

### Deploy

Once files are uploaded and secrets configured, the Space will automatically build and deploy.

## Example Output

```
================================================================================
AI REGULATORY COMPLIANCE AUDITOR - Inference Script
================================================================================
Model: gpt-4
API Base URL: https://api.openai.com/v1
Temperature: 0
Max Tokens: 4000
================================================================================

Initializing OpenAI client...
Initializing Compliance Auditor Environment...
Available Tasks: ['easy', 'medium', 'hard']

================================================================================
Starting Task: EASY
================================================================================
Task Description: Review the privacy policy and identify missing mandatory clauses required under GDPR.
Max Steps: 5
Document Length: 3245 characters

--- Step 1/5 ---
Calling LLM for analysis...
LLM Response Length: 1523 characters
Findings submitted: 2
Reward: 0.7500
Cumulative Reward: 0.7500
Correct Findings: 2
False Positives: 0
Missed Violations: 0

--- Task EASY Complete ---
Final Score: 0.7500
Total Findings: 2

================================================================================
Starting Task: MEDIUM
================================================================================
Task Description: Review the data privacy framework and identify contradictions between sections.
Max Steps: 8
Document Length: 4892 characters

--- Step 1/8 ---
Calling LLM for analysis...
LLM Response Length: 2134 characters
Findings submitted: 4
Reward: 0.8125
Cumulative Reward: 0.8125
Correct Findings: 4
False Positives: 0
Missed Violations: 0

--- Task MEDIUM Complete ---
Final Score: 0.8125
Total Findings: 4

================================================================================
Starting Task: HARD
================================================================================
Task Description: Perform comprehensive multi-document compliance audit.
Max Steps: 15
Document Length: 12456 characters

--- Step 1/15 ---
Calling LLM for analysis...
LLM Response Length: 3421 characters
Findings submitted: 8
Reward: 0.6500
Cumulative Reward: 0.6500
Correct Findings: 7
False Positives: 1
Missed Violations: 3

--- Step 2/15 ---
Calling LLM for analysis...
LLM Response Length: 1234 characters
Findings submitted: 3
Reward: 0.2250
Cumulative Reward: 0.8750
Correct Findings: 2
False Positives: 0
Missed Violations: 1

--- Task HARD Complete ---
Final Score: 0.7250
Total Findings: 11

================================================================================
FINAL RESULTS SUMMARY
================================================================================

Task: EASY
  Final Score: 0.7500
  Steps Taken: 1
  Findings: 2
  Correct: 2
  False Positives: 0

Task: MEDIUM
  Final Score: 0.8125
  Steps Taken: 1
  Findings: 4
  Correct: 4
  False Positives: 0

Task: HARD
  Final Score: 0.7250
  Steps Taken: 2
  Findings: 11
  Correct: 9
  False Positives: 1

================================================================================
AVERAGE SCORE: 0.7625
================================================================================

Results saved to: inference_results.json
```

## Project Structure

```
ai_regulatory_compliance_auditor/
├── openenv.yaml           # OpenEnv specification
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── README.md             # This file
├── inference.py          # Inference script with OpenAI client
└── src/
    ├── __init__.py       # Package initialization
    ├── models.py         # Pydantic models (Observation, Action, Reward)
    ├── documents.py      # Document corpus with embedded violations
    ├── tasks.py          # Task definitions with ground truth
    ├── graders.py        # Deterministic grading logic
    └── environment.py    # Main OpenEnv environment class
```

## Key Components

### `src/models.py`
Pydantic models defining the typed structures for:
- `Observation`: What the agent sees
- `Action`: What the agent submits
- `Reward`: Scoring breakdown
- `ComplianceFinding`: Individual violation
- `State`: Full environment state

### `src/documents.py`
Realistic regulatory documents:
- Privacy policies
- Data processing agreements
- Cookie policies
- Data retention policies

### `src/tasks.py`
Three task definitions with:
- Ground truth violations
- Difficulty levels
- Scoring weights

### `src/graders.py`
Deterministic grading with:
- Similarity-based matching
- Partial credit for related violations
- Severity scoring
- Repetition detection

### `src/environment.py`
OpenEnv-compliant environment implementing:
- `reset(task_id)`: Initialize new episode
- `step(action)`: Process findings and return reward
- `state()`: Get full internal state

## Resource Requirements

- **CPU**: 2 cores minimum
- **Memory**: 8 GB RAM maximum
- **Runtime**: Under 20 minutes for all tasks
- **Storage**: ~50 MB for code and documents

## Constraints

- **No API calls inside environment**: Grading is fully local
- **No randomness**: Fully reproducible results
- **Deterministic matching**: Same input always produces same output

## Contributing

Contributions are welcome! Areas for improvement:

1. Additional regulatory frameworks (HIPAA, SOX, etc.)
2. More complex multi-document scenarios
3. Enhanced matching algorithms
4. Additional violation types
5. Performance optimizations

## License

MIT License - See LICENSE file for details.

## Citation

If you use this environment in your research, please cite:

```bibtex
@software{compliance_auditor_2024,
  title={AI Regulatory Compliance Auditor: An OpenEnv Environment},
  author={AI Compliance Auditor Team},
  year={2024},
  version={1.0.0}
}
```

## Support

For issues, questions, or contributions, please open an issue in the project repository.