"""
AI Regulatory Compliance Auditor - OpenEnv Environment.
Complete environment implementation with models, documents, tasks, and graders.
"""

import hashlib
import json
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
from difflib import SequenceMatcher
from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class SeverityLevel(str, Enum):
    """Severity levels for compliance violations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ViolationType(str, Enum):
    """Types of regulatory compliance violations."""
    MISSING_MANDATORY_CLAUSE = "missing_mandatory_clause"
    DATA_RETENTION_VIOLATION = "data_retention_violation"
    CONSENT_REQUIREMENT_VIOLATION = "consent_requirement_violation"
    CROSS_BORDER_TRANSFER_VIOLATION = "cross_border_transfer_violation"
    DATA_SUBJECT_RIGHTS_VIOLATION = "data_subject_rights_violation"
    PURPOSE_LIMITATION_VIOLATION = "purpose_limitation_violation"
    DATA_MINIMIZATION_VIOLATION = "data_minimization_violation"
    SECURITY_MEASURES_VIOLATION = "security_measures_violation"
    BREACH_NOTIFICATION_VIOLATION = "breach_notification_violation"
    THIRD_PARTY_SHARING_VIOLATION = "third_party_sharing_violation"
    CHILDREN_DATA_VIOLATION = "children_data_violation"
    AUTOMATED_DECISION_VIOLATION = "automated_decision_violation"
    DOCUMENT_CONTRADICTION = "document_contradiction"
    REGULATORY_MISMATCH = "regulatory_mismatch"


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ComplianceFinding(BaseModel):
    """A single compliance finding identified by the auditor."""
    violation_type: ViolationType
    severity: SeverityLevel
    location: str
    description: str
    evidence: str
    regulatory_reference: Optional[str] = None


class Observation(BaseModel):
    """Observation provided to the agent at each step."""
    document_text: str
    step_count: int
    max_steps: int
    task_id: str
    task_description: str
    previous_findings: List[ComplianceFinding] = []
    previous_rewards: List[float] = []
    is_final: bool = False


class Action(BaseModel):
    """Action submitted by the agent."""
    findings: List[ComplianceFinding] = []
    is_submission: bool = False
    reasoning: Optional[str] = None


class RewardBreakdown(BaseModel):
    """Detailed breakdown of reward calculation."""
    correct_findings: int = 0
    false_positives: int = 0
    missed_violations: int = 0
    correct_severity_count: int = 0
    base_score: float = 0.0
    severity_bonus: float = 0.0
    false_positive_penalty: float = 0.0
    repetition_penalty: float = 0.0
    total_raw_score: float = 0.0


class Reward(BaseModel):
    """Reward returned after each step."""
    score: float
    raw_score: float
    breakdown: RewardBreakdown
    feedback: str


class State(BaseModel):
    """Full internal state of the environment."""
    current_task_id: str
    current_document: str
    ground_truth: List[ComplianceFinding]
    step_count: int
    max_steps: int
    all_findings: List[ComplianceFinding] = []
    cumulative_reward: float = 0.0
    episode_complete: bool = False
    submission_history: List[str] = []


class TaskDefinition(BaseModel):
    """Definition of a compliance auditing task."""
    task_id: str
    difficulty: str
    description: str
    document_text: str
    ground_truth: List[ComplianceFinding]
    max_steps: int
    scoring_weights: Dict[str, float] = {
        "correct_finding": 1.0,
        "severity_bonus": 0.25,
        "false_positive_penalty": -0.5,
        "repetition_penalty": -0.1
    }


# =============================================================================
# DOCUMENTS
# =============================================================================

TASK_1_DOCUMENT = """
PRIVACY POLICY - TechFlow Solutions Inc.
Effective Date: January 15, 2024

1. INTRODUCTION
TechFlow Solutions Inc. ("Company", "we", "us", or "our") is committed to protecting 
the privacy and security of your personal data. This Privacy Policy describes how we 
collect, use, process, and disclose your information when you use our services.

2. DATA CONTROLLER INFORMATION
The data controller responsible for your personal data is:
TechFlow Solutions Inc.
123 Innovation Drive, Suite 400
San Francisco, CA 94105
Email: privacy@techflowsolutions.com

3. INFORMATION WE COLLECT
We collect the following types of personal data:
- Account information (name, email address, phone number)
- Profile information (job title, company name)
- Usage data (how you interact with our services)
- Device information (IP address, browser type, operating system)
- Payment information (credit card details, billing address)

4. PURPOSE OF DATA PROCESSING
We process your personal data for the following purposes:
- Providing and maintaining our services
- Processing transactions and sending related information
- Sending technical notices and support messages
- Responding to your comments and questions
- Improving our services and developing new features
- Marketing and promotional communications

5. LEGAL BASIS FOR PROCESSING
We process your personal data based on:
- Performance of a contract with you
- Our legitimate interests in operating and improving our business
- Compliance with legal obligations

6. DATA SHARING AND THIRD PARTIES
We may share your personal data with:
- Service providers who assist in our operations
- Business partners for joint offerings
- Law enforcement when required by law
- In connection with a merger, acquisition, or sale of assets

7. INTERNATIONAL DATA TRANSFERS
Your personal data may be transferred to and processed in countries outside of your 
residence. We ensure appropriate safeguards are in place for such transfers.

8. DATA SECURITY
We implement appropriate technical and organizational measures to protect your 
personal data against unauthorized access, alteration, disclosure, or destruction.

9. YOUR RIGHTS
Under applicable data protection laws, you have the right to:
- Access your personal data
- Rectify inaccurate personal data
- Erase your personal data
- Restrict processing of your personal data
- Data portability
- Object to processing of your personal data

To exercise these rights, contact us at privacy@techflowsolutions.com.

10. CHANGES TO THIS POLICY
We may update this Privacy Policy from time to time. We will notify you of any 
changes by posting the new Privacy Policy on this page.

11. CONTACT US
If you have questions about this Privacy Policy, please contact us at:
Email: privacy@techflowsolutions.com
Phone: +1 (555) 123-4567

Last Updated: January 15, 2024
"""

TASK_2_DOCUMENT = """
COMPREHENSIVE DATA PRIVACY FRAMEWORK
DataStream Analytics Corp.
Version 2.3 - March 2024

================================================================================
SECTION A: CONSENT AND LEGAL BASIS FOR PROCESSING
================================================================================

A.1 GENERAL CONSENT REQUIREMENTS
DataStream Analytics Corp. ("Company") processes personal data only with valid 
legal basis as required by the General Data Protection Regulation (GDPR) and 
other applicable privacy laws.

A.2 CONSENT OBTAINED
For all data processing activities, we obtain explicit, informed, and freely given 
consent from data subjects before collecting or processing their personal data. 
Consent is obtained through:
- Clear affirmative action (opt-in checkboxes)
- Detailed explanation of processing purposes
- Easy withdrawal mechanism

A.3 LEGITIMATE INTEREST ASSESSMENT
Where we rely on legitimate interests as our legal basis, we conduct a Legitimate 
Interest Assessment (LIA) to ensure our interests do not override your fundamental 
rights and freedoms.

A.4 MARKETING COMMUNICATIONS
We send marketing communications only to individuals who have provided explicit 
opt-in consent. You may withdraw consent at any time by clicking the unsubscribe 
link in our emails or contacting our privacy team.

================================================================================
SECTION B: DIRECT MARKETING AND PROMOTIONAL ACTIVITIES
================================================================================

B.1 EMAIL MARKETING
By creating an account with DataStream Analytics Corp., you automatically agree 
to receive promotional emails, newsletters, and marketing materials. We may send 
you information about our products, services, special offers, and partner promotions.

B.2 THIRD-PARTY MARKETING
We may share your contact information with our marketing partners so they can 
send you relevant offers and promotions. This sharing occurs automatically unless 
you explicitly opt-out by sending a written request to privacy@datastream.com.

B.3 BEHAVIORAL ADVERTISING
We use your browsing history and purchase behavior to deliver personalized 
advertisements. This processing is based on your acceptance of our terms of service 
and does not require separate consent.

B.4 TELEMARKETING
We reserve the right to contact you via telephone for promotional purposes. 
Your phone number may be shared with our telemarketing partners without additional 
consent as part of our service provision.

================================================================================
SECTION C: DATA PROCESSING OPERATIONS
================================================================================

C.1 CATEGORIES OF DATA PROCESSED
We process the following categories of personal data:
- Identity data (name, username, date of birth)
- Contact data (email, phone, address)
- Financial data (payment card details, transaction history)
- Technical data (IP address, login data, browser type)
- Profile data (preferences, feedback, survey responses)
- Usage data (how you use our website and services)
- Marketing data (communication preferences, consent records)

C.2 PURPOSES OF PROCESSING
- Service delivery and customer support
- Payment processing and fraud prevention
- Product improvement and analytics
- Marketing and advertising (with consent where required)
- Legal compliance and regulatory obligations

================================================================================
SECTION D: DATA RETENTION
================================================================================

D.1 RETENTION PERIODS
We retain personal data for as long as necessary to fulfill the purposes outlined 
in this policy, unless a longer retention period is required by law.

- Account data: Duration of account plus 3 years
- Transaction data: 7 years for tax and accounting purposes
- Marketing data: Until consent is withdrawn
- Technical logs: 12 months

================================================================================
SECTION E: YOUR RIGHTS
================================================================================

E.1 DATA SUBJECT RIGHTS
You have the right to access, rectify, erase, restrict, port, and object to the 
processing of your personal data. To exercise these rights, contact our Data 
Protection Officer at dpo@datastream.com.

E.2 RESPONSE TIME
We will respond to your rights requests within 30 days.

================================================================================
SECTION F: CONTACT INFORMATION
================================================================================

Data Protection Officer
DataStream Analytics Corp.
456 Privacy Lane, Suite 200
Boston, MA 02101
Email: dpo@datastream.com
Phone: +1 (555) 987-6543

Document Version: 2.3
Last Updated: March 15, 2024
"""

TASK_3_DOCUMENT = """TASK 3: MULTI-DOCUMENT COMPLIANCE AUDIT

You are reviewing three related documents from CloudSync Technologies Inc. 
Your task is to identify compliance violations across all documents and detect 
any contradictions or inconsistencies between them.

================================================================================
DOCUMENT 1: DATA PROCESSING AGREEMENT
================================================================================
GLOBAL DATA PROCESSING AGREEMENT
CloudSync Technologies Inc.
Document ID: DPA-2024-001
Effective Date: February 1, 2024

PARTIES
Data Controller: CloudSync Technologies Inc. ("Controller")
Data Processor: GlobalTech Services Ltd. ("Processor")

1. DEFINITIONS
1.1 "Personal Data" means any information relating to an identified or identifiable 
natural person processed under this Agreement.
1.2 "Data Protection Laws" means GDPR, CCPA, and all applicable data protection 
legislation.
1.3 "Sub-processor" means any third party appointed by the Processor to process 
Personal Data.

2. SCOPE OF PROCESSING
2.1 The Processor shall process Personal Data on behalf of the Controller for:
- Cloud storage and backup services
- Data analytics and business intelligence
- Customer relationship management
- Email marketing automation

2.2 Categories of data subjects: Employees, customers, prospects, business partners
2.3 Types of personal data: Names, emails, phone numbers, addresses, employment 
details, purchase history, browsing behavior

3. PROCESSOR OBLIGATIONS
3.1 The Processor shall process Personal Data only on documented instructions from 
the Controller.
3.2 The Processor shall implement appropriate technical and organizational measures.
3.3 The Processor shall promptly notify the Controller of any personal data breach 
within 72 hours of becoming aware.
3.4 The Processor may engage Sub-processors provided that:
- The Controller is informed of any changes
- The Processor imposes the same data protection obligations
- The Processor remains fully liable for Sub-processor performance

4. INTERNATIONAL TRANSFERS
4.1 The Processor may transfer Personal Data to countries outside the EEA provided 
that appropriate safeguards are in place, including:
- Standard Contractual Clauses (SCCs)
- Binding Corporate Rules
- Adequacy decisions

4.2 The Processor maintains data centers in:
- Ireland (Primary)
- United States (Secondary)
- Singapore (Backup)
- Brazil (Regional processing)

5. DATA SUBJECT RIGHTS
5.1 The Processor shall assist the Controller in responding to data subject requests.
5.2 The Processor shall maintain records of processing activities.

6. AUDIT RIGHTS
6.1 The Controller may audit the Processor's compliance with this Agreement.
6.2 Audits shall be conducted with reasonable notice and during normal business hours.

7. TERM AND TERMINATION
7.1 This Agreement shall remain in effect for the duration of the underlying 
services agreement.
7.2 Upon termination, the Processor shall delete or return all Personal Data.

================================================================================
DOCUMENT 2: COOKIE POLICY
================================================================================
CLOUDSYNC TECHNOLOGIES - COOKIE POLICY
Last Updated: January 20, 2024

1. WHAT ARE COOKIES?
Cookies are small text files placed on your device when you visit our website.

2. TYPES OF COOKIES WE USE
2.1 STRICTLY NECESSARY COOKIES
Cookie Name: session_id, Purpose: Maintains user session, Duration: Session
Cookie Name: auth_token, Purpose: Authentication, Duration: 24 hours

2.2 PERFORMANCE COOKIES
Cookie Name: _ga, Provider: Google Analytics, Purpose: Analytics, Duration: 2 years
Cookie Name: _gid, Provider: Google Analytics, Purpose: Analytics, Duration: 24 hours

2.3 FUNCTIONALITY COOKIES
Cookie Name: user_prefs, Purpose: Stores user preferences, Duration: 1 year
Cookie Name: language, Purpose: Language selection, Duration: 1 year

2.4 TARGETING/ADVERTISING COOKIES
Cookie Name: _fbp, Provider: Facebook, Purpose: Advertising, Duration: 3 months
Cookie Name: ad_preferences, Purpose: Ad personalization, Duration: 6 months

3. CONSENT MANAGEMENT
3.1 We obtain your consent before placing non-essential cookies on your device.
3.2 Our cookie consent banner appears on your first visit and allows you to:
- Accept all cookies
- Reject non-essential cookies
- Customize your preferences

4. THIRD-PARTY COOKIES
4.1 Some cookies are placed by third-party services that appear on our pages.
4.2 We use: Google Analytics, Facebook Pixel, HubSpot, Intercom
4.3 We do not control these third-party cookies.

5. CONTACT US
Email: privacy@cloudsynctech.com
Phone: +1 (555) 234-5678

================================================================================
DOCUMENT 3: DATA RETENTION POLICY
================================================================================
CLOUDSYNC TECHNOLOGIES - DATA RETENTION POLICY
Policy Number: DRP-2024-003
Effective Date: March 1, 2024

1. PURPOSE AND SCOPE
1.1 This policy establishes guidelines for the retention and disposal of personal 
data processed by CloudSync Technologies Inc.

2. RETENTION SCHEDULE
2.1 CUSTOMER DATA
- Account information: Duration of account + 7 years
- Transaction records: 10 years
- Support tickets: 5 years
- Usage logs: 2 years

2.2 EMPLOYEE DATA
- Personnel records: Employment + 10 years
- Payroll data: 7 years
- Performance reviews: 5 years

2.3 MARKETING DATA
- Consent records: Duration of consent + 5 years
- Email lists: Until opt-out
- Campaign analytics: 3 years

2.4 TECHNICAL DATA
- Server logs: 90 days
- Error logs: 1 year
- Backup data: 30 days

3. DATA DISPOSAL
3.1 Upon expiration, data shall be securely deleted or anonymized.
3.2 Disposal methods: Secure deletion, physical destruction, anonymization.

4. CONTACT
Data Protection Officer
Email: dpo@cloudsynctech.com
Phone: +1 (555) 234-5678
"""

def get_document(task_id: str) -> str:
    """Retrieve document for a specific task."""
    return {
        "easy": TASK_1_DOCUMENT,
        "medium": TASK_2_DOCUMENT,
        "hard": TASK_3_DOCUMENT
    }[task_id]


# =============================================================================
# GRADING FUNCTIONS
# =============================================================================

def compute_finding_hash(finding: ComplianceFinding) -> str:
    """Compute deterministic hash for duplicate detection."""
    content = f"{finding.violation_type.value}|{finding.severity.value}|{finding.location}|{finding.description}"
    return hashlib.sha256(content.encode()).hexdigest()


def compute_similarity(text1: str, text2: str) -> float:
    """Compute text similarity ratio."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def _are_related_violations(type1: ViolationType, type2: ViolationType) -> bool:
    """Check if violation types are related."""
    related_groups = [
        {ViolationType.MISSING_MANDATORY_CLAUSE, ViolationType.DATA_SUBJECT_RIGHTS_VIOLATION},
        {ViolationType.CONSENT_REQUIREMENT_VIOLATION, ViolationType.DOCUMENT_CONTRADICTION},
        {ViolationType.DATA_RETENTION_VIOLATION, ViolationType.PURPOSE_LIMITATION_VIOLATION},
        {ViolationType.CROSS_BORDER_TRANSFER_VIOLATION, ViolationType.REGULATORY_MISMATCH},
        {ViolationType.THIRD_PARTY_SHARING_VIOLATION, ViolationType.DATA_MINIMIZATION_VIOLATION},
    ]
    for group in related_groups:
        if type1 in group and type2 in group:
            return True
    return False


def match_finding_to_ground_truth(
    finding: ComplianceFinding,
    ground_truth: List[ComplianceFinding],
    match_threshold: float = 0.6
) -> Tuple[bool, int, float]:
    """Match finding to ground truth with similarity scoring."""
    best_match_idx = -1
    best_match_score = 0.0
    
    for idx, gt in enumerate(ground_truth):
        score = 0.0
        if finding.violation_type == gt.violation_type:
            score += 0.4
        elif _are_related_violations(finding.violation_type, gt.violation_type):
            score += 0.2
        else:
            continue
        
        location_sim = compute_similarity(finding.location, gt.location)
        score += location_sim * 0.3
        
        desc_sim = max(
            compute_similarity(finding.description, gt.description),
            compute_similarity(finding.evidence, gt.evidence),
            compute_similarity(finding.description, gt.evidence),
            compute_similarity(finding.evidence, gt.description)
        )
        score += desc_sim * 0.3
        
        if score > best_match_score:
            best_match_score = score
            best_match_idx = idx
    
    return best_match_score >= match_threshold, best_match_idx, best_match_score


def score_severity_match(finding_severity: SeverityLevel, gt_severity: SeverityLevel) -> float:
    """Score severity classification accuracy."""
    if finding_severity == gt_severity:
        return 1.0
    
    severity_order = [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]
    distance = abs(severity_order.index(finding_severity) - severity_order.index(gt_severity))
    return {1: 0.5, 2: 0.25}.get(distance, 0.0)


def grade_findings(
    agent_findings: List[ComplianceFinding],
    ground_truth: List[ComplianceFinding],
    scoring_weights: Dict[str, float],
    submission_history: List[str]
) -> Tuple[Reward, List[str], List[int], List[int]]:
    """Grade agent findings against ground truth."""
    matched_gt_indices = set()
    total_correct = 0
    total_severity_bonus = 0.0
    total_false_positives = 0
    total_repetition_penalty = 0.0
    new_hashes = []
    feedback_parts = []
    
    for finding in agent_findings:
        finding_hash = compute_finding_hash(finding)
        new_hashes.append(finding_hash)
        
        if finding_hash in submission_history:
            total_repetition_penalty += abs(scoring_weights["repetition_penalty"])
            continue
        
        is_match, gt_idx, _ = match_finding_to_ground_truth(finding, ground_truth)
        
        if is_match and gt_idx not in matched_gt_indices:
            matched_gt_indices.add(gt_idx)
            total_correct += 1
            severity_score = score_severity_match(finding.severity, ground_truth[gt_idx].severity)
            if severity_score >= 0.5:
                total_severity_bonus += scoring_weights["severity_bonus"] * severity_score
            feedback_parts.append(f"Correct: {finding.description[:50]}...")
        elif not is_match:
            total_false_positives += 1
            feedback_parts.append(f"False positive: {finding.description[:50]}...")
    
    missed_indices = [i for i in range(len(ground_truth)) if i not in matched_gt_indices]
    
    base_score = total_correct * scoring_weights["correct_finding"]
    fp_penalty = total_false_positives * abs(scoring_weights["false_positive_penalty"])
    raw_score = base_score + total_severity_bonus - fp_penalty - total_repetition_penalty
    
    max_score = len(ground_truth) * (scoring_weights["correct_finding"] + scoring_weights["severity_bonus"])
    normalized_score = max(0.0, min(1.0, raw_score / max_score)) if max_score > 0 else 0.0
    
    breakdown = RewardBreakdown(
        correct_findings=total_correct,
        false_positives=total_false_positives,
        missed_violations=len(missed_indices),
        correct_severity_count=int(total_severity_bonus / scoring_weights["severity_bonus"]) if scoring_weights["severity_bonus"] > 0 else 0,
        base_score=base_score,
        severity_bonus=total_severity_bonus,
        false_positive_penalty=-fp_penalty,
        repetition_penalty=total_repetition_penalty,
        total_raw_score=raw_score
    )
    
    feedback = " | ".join(feedback_parts) if feedback_parts else "No findings."
    feedback += f" | Correct: {total_correct}/{len(ground_truth)}, FP: {total_false_positives}"
    
    return Reward(score=normalized_score, raw_score=raw_score, breakdown=breakdown, feedback=feedback), new_hashes, list(matched_gt_indices), missed_indices


# =============================================================================
# TASK DEFINITIONS
# =============================================================================

def get_task_definition(task_id: str) -> TaskDefinition:
    """Get task definition by ID."""
    tasks = {
        "easy": TaskDefinition(
            task_id="easy",
            difficulty="easy",
            description="Review the privacy policy and identify missing mandatory clauses required under GDPR.",
            document_text=get_document("easy"),
            ground_truth=[
                ComplianceFinding(
                    violation_type=ViolationType.MISSING_MANDATORY_CLAUSE,
                    severity=SeverityLevel.HIGH,
                    location="Section 9: YOUR RIGHTS",
                    description="Missing mandatory right to lodge a complaint with a supervisory authority.",
                    evidence="Section 9 lists rights but does not include complaint right.",
                    regulatory_reference="GDPR Article 77"
                ),
                ComplianceFinding(
                    violation_type=ViolationType.MISSING_MANDATORY_CLAUSE,
                    severity=SeverityLevel.HIGH,
                    location="Entire Document",
                    description="Missing Data Protection Officer (DPO) contact information.",
                    evidence="No DPO designated despite data processing at scale.",
                    regulatory_reference="GDPR Articles 37-39"
                )
            ],
            max_steps=5
        ),
        "medium": TaskDefinition(
            task_id="medium",
            difficulty="medium",
            description="Review the data privacy framework and identify contradictions between sections.",
            document_text=get_document("medium"),
            ground_truth=[
                ComplianceFinding(
                    violation_type=ViolationType.DOCUMENT_CONTRADICTION,
                    severity=SeverityLevel.CRITICAL,
                    location="Section A.4 vs Section B.1",
                    description="Contradiction: A.4 requires opt-in, B.1 auto-enrolls on account creation.",
                    evidence="A.4: 'explicit opt-in consent' vs B.1: 'automatically agree'",
                    regulatory_reference="GDPR Article 6(1)(a)"
                ),
                ComplianceFinding(
                    violation_type=ViolationType.DOCUMENT_CONTRADICTION,
                    severity=SeverityLevel.HIGH,
                    location="Section A.2 vs Section B.2",
                    description="Contradiction: A.2 requires explicit consent, B.2 allows automatic sharing.",
                    evidence="A.2: 'explicit consent' vs B.2: 'automatically unless opt-out'",
                    regulatory_reference="GDPR Article 7"
                ),
                ComplianceFinding(
                    violation_type=ViolationType.CONSENT_REQUIREMENT_VIOLATION,
                    severity=SeverityLevel.HIGH,
                    location="Section B.3",
                    description="Behavioral advertising uses ToS acceptance instead of consent.",
                    evidence="B.3: 'based on acceptance of terms of service'",
                    regulatory_reference="ePrivacy Directive Article 5(3)"
                ),
                ComplianceFinding(
                    violation_type=ViolationType.CONSENT_REQUIREMENT_VIOLATION,
                    severity=SeverityLevel.HIGH,
                    location="Section B.4",
                    description="Telemarketing without additional consent.",
                    evidence="B.4: 'without additional consent as part of service provision'",
                    regulatory_reference="GDPR Article 6(1)(a)"
                )
            ],
            max_steps=8
        ),
        "hard": TaskDefinition(
            task_id="hard",
            difficulty="hard",
            description="Perform comprehensive multi-document compliance audit of CloudSync Technologies.",
            document_text=get_document("hard"),
            ground_truth=[
                ComplianceFinding(violation_type=ViolationType.BREACH_NOTIFICATION_VIOLATION, severity=SeverityLevel.HIGH, location="DPA Section 3.3", description="Incomplete breach notification - missing supervisory authority notification.", evidence="Only mentions 72-hour Controller notification.", regulatory_reference="GDPR Articles 33-34"),
                ComplianceFinding(violation_type=ViolationType.MISSING_MANDATORY_CLAUSE, severity=SeverityLevel.MEDIUM, location="DPA Section 3.4", description="No specific sub-processor list maintained.", evidence="Allows sub-processors without list.", regulatory_reference="GDPR Article 28(2)"),
                ComplianceFinding(violation_type=ViolationType.CROSS_BORDER_TRANSFER_VIOLATION, severity=SeverityLevel.HIGH, location="DPA Section 4.2", description="Brazil transfer lacks legal basis - no EU adequacy decision.", evidence="Brazil listed but no adequacy decision.", regulatory_reference="GDPR Articles 44-49"),
                ComplianceFinding(violation_type=ViolationType.CONSENT_REQUIREMENT_VIOLATION, severity=SeverityLevel.HIGH, location="Cookie Policy Section 2.4", description="Advertising cookies without granular consent.", evidence="Targeting cookies listed without per-cookie consent.", regulatory_reference="ePrivacy Directive Article 5(3)"),
                ComplianceFinding(violation_type=ViolationType.THIRD_PARTY_SHARING_VIOLATION, severity=SeverityLevel.MEDIUM, location="Cookie Policy Section 4", description="Insufficient third-party cookie disclosure.", evidence="Defers to third-party policies.", regulatory_reference="GDPR Article 13(1)(e)"),
                ComplianceFinding(violation_type=ViolationType.DATA_RETENTION_VIOLATION, severity=SeverityLevel.MEDIUM, location="Retention Section 2.1", description="Excessive account data retention (7 years).", evidence="'Duration + 7 years' may exceed requirements.", regulatory_reference="GDPR Article 5(1)(e)"),
                ComplianceFinding(violation_type=ViolationType.DATA_RETENTION_VIOLATION, severity=SeverityLevel.MEDIUM, location="Retention Section 2", description="Missing cookie data retention periods.", evidence="No category for cookie/tracking data.", regulatory_reference="GDPR Article 5(1)(e)"),
                ComplianceFinding(violation_type=ViolationType.REGULATORY_MISMATCH, severity=SeverityLevel.HIGH, location="Cross-Document", description="Sub-processor disclosure inconsistency between DPA and Cookie Policy.", evidence="Cookie Policy uses third parties not linked to DPA.", regulatory_reference="GDPR Article 28(4)"),
                ComplianceFinding(violation_type=ViolationType.REGULATORY_MISMATCH, severity=SeverityLevel.HIGH, location="Cross-Document", description="Retention periods conflict with DPA termination obligations.", evidence="DPA requires deletion but retention is 7-10 years.", regulatory_reference="GDPR Article 28(3)(g)"),
                ComplianceFinding(violation_type=ViolationType.REGULATORY_MISMATCH, severity=SeverityLevel.MEDIUM, location="Cross-Document", description="Cookie consent conflicts with DPA documented instructions.", evidence="Cookie deployment without clear Controller instructions.", regulatory_reference="GDPR Article 28(3)(a)")
            ],
            max_steps=15
        )
    }
    return tasks[task_id]


# =============================================================================
# MAIN ENVIRONMENT CLASS
# =============================================================================

class ComplianceAuditorEnvironment:
    """OpenEnv-compliant environment for compliance auditing."""
    
    def __init__(self):
        self.current_task: Optional[TaskDefinition] = None
        self.step_count: int = 0
        self.max_steps: int = 5
        self.all_findings: List[ComplianceFinding] = []
        self.submission_history: List[str] = []
        self.step_rewards: List[float] = []
        self.cumulative_reward: float = 0.0
        self.episode_complete: bool = False
        self.initialized: bool = False
    
    def reset(self, task_id: str = "easy") -> Observation:
        """Reset environment for new episode."""
        self.current_task = get_task_definition(task_id)
        self.step_count = 0
        self.max_steps = self.current_task.max_steps
        self.all_findings = []
        self.submission_history = []
        self.step_rewards = []
        self.cumulative_reward = 0.0
        self.episode_complete = False
        self.initialized = True
        
        return Observation(
            document_text=self.current_task.document_text,
            step_count=0,
            max_steps=self.max_steps,
            task_id=self.current_task.task_id,
            task_description=self.current_task.description,
            previous_findings=[],
            previous_rewards=[],
            is_final=False
        )
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """Execute one step in the environment."""
        if not self.initialized:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        
        self.step_count += 1
        is_final = self.step_count >= self.max_steps or action.is_submission
        
        reward_obj, new_hashes, matched, missed = grade_findings(
            action.findings,
            self.current_task.ground_truth,
            self.current_task.scoring_weights,
            self.submission_history
        )
        
        self.submission_history.extend(new_hashes)
        self.all_findings.extend(action.findings)
        self.step_rewards.append(reward_obj.score)
        self.cumulative_reward += reward_obj.score
        self.episode_complete = is_final
        
        observation = Observation(
            document_text=self.current_task.document_text,
            step_count=self.step_count,
            max_steps=self.max_steps,
            task_id=self.current_task.task_id,
            task_description=self.current_task.description,
            previous_findings=self.all_findings,
            previous_rewards=self.step_rewards,
            is_final=is_final
        )
        
        info = {
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "is_submission": action.is_submission,
            "reward_breakdown": reward_obj.breakdown.model_dump(),
            "matched_ground_truth_indices": matched,
            "missed_violations_count": len(missed),
            "cumulative_reward": self.cumulative_reward,
            "episode_complete": is_final
        }
        
        return observation, reward_obj.score, is_final, info
    
    def state(self) -> Dict[str, Any]:
        """Return full internal state."""
        if not self.initialized:
            raise RuntimeError("Environment not initialized.")
        
        return State(
            current_task_id=self.current_task.task_id,
            current_document=self.current_task.document_text,
            ground_truth=self.current_task.ground_truth,
            step_count=self.step_count,
            max_steps=self.max_steps,
            all_findings=self.all_findings,
            cumulative_reward=self.cumulative_reward,
            episode_complete=self.episode_complete,
            submission_history=self.submission_history
        ).model_dump()
    
    def get_available_tasks(self) -> List[Dict[str, Any]]:
        """Get list of available tasks."""
        return [
            {"task_id": t, "difficulty": t, "description": get_task_definition(t).description, "max_steps": get_task_definition(t).max_steps, "ground_truth_count": len(get_task_definition(t).ground_truth)}
            for t in ["easy", "medium", "hard"]
        ]