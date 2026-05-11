---
name: hr-learning-development-pack
description: Support-only HR and L&D orchestration pack with explicit anti-discrimination, fairness, and human-review controls for employment-impacting insights.
---

# HR & Learning Development Pack

## Covered Skills (MB-P2-006)
- hr-management
- workforce-planning
- hiring-pipeline-intelligence
- job-description-generation
- interview-scorecard-analysis
- onboarding-workflow-management
- employee-record-management
- performance-coaching-support
- learning-development
- skills-gap-analysis
- role-based-learning-paths
- onboarding-curriculum-design
- training-content-generation
- learning-assessment-design
- certification-tracking
- coaching-plan-generation
- learning-roi-analysis

## Mandatory Governance
- **Support only**: Never make autonomous hiring, firing, compensation, promotion, or disciplinary determinations.
- **Protected-attribute exclusion**: Scoring/ranking/fit calculations must not ingest or derive from protected attributes.
- **Fairness checks required**: subgroup disparity checks and adverse-impact screening are required before recommendations are released.
- **Human decision gate**: Any performance-related output that could affect employment terms must be routed to human review with documented rationale and sign-off.

## Protected/Sensitive Attribute Policy
The following fields are prohibited in score features, either directly or via proxy features:
- age, date_of_birth
- race, ethnicity, color, caste, tribe
- sex, gender identity, sexual orientation
- disability, medical/genetic status
- religion, creed
- pregnancy/parental/family status
- nationality/citizenship/immigration status
- veteran status

If present in source records, these must be redacted before model feature extraction and retained only for authorized fairness auditing.

## L&D Outcome Tracking
- Track planned vs achieved competency outcomes by role cohort.
- Track learning completion, assessment score deltas, manager validation, and on-the-job evidence.
- Track certification lifecycle: assigned, in-progress, completed, expired, renewed.

## Certification Workflow
1. Assign certification requirement by role and effective date.
2. Generate due-date obligations and reminders.
3. Capture evidence artifact(s) and evaluator attestation.
4. Route non-compliance exceptions to human governance queue.
5. Emit auditable status transitions and renewal schedule.
