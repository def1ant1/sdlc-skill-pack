# Onboarding Tracks

Used by `skills/customer-success/SKILL.md` to select and generate onboarding sequences
by customer plan, industry, and team size.

---

## Track Selection Matrix

| Plan | Team Size | Industry | Track |
|---|---|---|---|
| Free / Starter | Any | Any | Self-Serve |
| Pro | 1–10 | Any | Guided-SMB |
| Pro | 11–50 | Any | Guided-SMB |
| Pro | 51+ | Any | Guided-Mid |
| Enterprise | Any | Developer Tools | Enterprise-Dev |
| Enterprise | Any | FinTech / Healthcare | Enterprise-Regulated |
| Enterprise | Any | Other | Enterprise-Standard |

---

## Track: Self-Serve

**Duration**: 14 days
**Contact ratio**: 0 human touch points (fully automated)

| Day | Trigger | Channel | Message |
|---|---|---|---|
| 0 | Account created | Email | Welcome + setup checklist |
| 1 | No setup complete | In-app | "Start here" tooltip sequence |
| 3 | First action taken | Email | "You're making progress" + next step |
| 7 | < 3 features used | Email | Feature highlight reel |
| 7 | ≥ 3 features used | Email | "Power user tips" |
| 14 | Setup < 50% | Email | "Need help?" + docs link |
| 14 | Setup ≥ 50% | Email | NPS survey (Day 30 scheduled) |

**Milestone gates**:
- `first_project_created` → unlock advanced features tooltip
- `first_output_generated` → trigger "share your result" prompt
- `invited_teammate` → trigger team plan upsell

---

## Track: Guided-SMB

**Duration**: 21 days
**Contact ratio**: 1 kickoff call + automated sequences

| Day | Trigger | Channel | Message |
|---|---|---|---|
| 0 | Account created | Email | Welcome + kickoff call booking link |
| 0–2 | Call not booked | Email | Reminder with async setup guide |
| 3 | Kickoff call completed | Email | Setup checklist + goals doc |
| 7 | Milestone: first output | Email | "Great start" + advanced tips |
| 7 | No first output | Email | "Stuck? Book a 15-min session" |
| 14 | Check-in | Email | Usage review + offer office hours |
| 21 | Onboarding close | Email | Graduation + NPS survey |

**CS touchpoints**:
- Kickoff call: 30 min; CS rep led; record goals in CRM
- Day 14 check-in: async email review; escalate if < 50% adoption

---

## Track: Guided-Mid

**Duration**: 30 days
**Contact ratio**: Kickoff + 2 check-ins + QBR scheduled

| Day | Trigger | Channel | Message |
|---|---|---|---|
| 0 | Account created | Email | Welcome + implementation guide |
| 1–3 | — | Call | Kickoff call: stakeholder mapping, goals, success metrics |
| 7 | — | Email | Week 1 progress report auto-generated |
| 14 | — | Call | Mid-point check-in: review adoption data |
| 21 | — | Email | Advanced use cases + integration docs |
| 30 | — | Call | Onboarding close call; schedule first QBR |

**Admin console setup required**: SSO, role configuration, data connectors.
**CS deliverable**: Customer Success Plan (CSP) document with named goals and KPIs.

---

## Track: Enterprise-Standard

**Duration**: 45 days
**Contact ratio**: Dedicated CSM, weekly syncs

| Week | Focus | Deliverable |
|---|---|---|
| 1 | Kickoff + stakeholder alignment | Project plan, RACI, success metrics |
| 2 | Technical setup + integration | Integration verified; admin trained |
| 3 | Pilot use case execution | First production workflow live |
| 4 | Adoption expansion | Team training sessions delivered |
| 5 | Review + optimization | Usage report; optimization recommendations |
| 6 | Graduation + QBR scheduled | Success criteria review; roadmap preview |

---

## Track: Enterprise-Regulated

**Duration**: 60 days
**Additional requirements**:
- Data Processing Agreement (DPA) signed before onboarding
- Security review completed (connector security classification audit)
- Compliance documentation package delivered (SOC2 report, GDPR DPA, HIPAA BAA if applicable)
- All data flows approved by customer security team

**Sequence**: Same as Enterprise-Standard with compliance gates at Week 1 and Week 3.

---

## Track: Enterprise-Dev

**Duration**: 30 days
**Developer-focused additions**:

| Week | Focus |
|---|---|
| 1 | API access + SDK setup; sandbox environment |
| 2 | First integration built; webhook testing |
| 3 | Production integration; observability setup |
| 4 | Developer advocacy: blog post, case study offer |

---

## Fallback Nudge Rules

If any milestone is not hit within the expected window, trigger a fallback:

| Milestone Missed | Days Late | Fallback Action |
|---|---|---|
| Kickoff call not booked | +3 | Async onboarding guide + Loom walkthrough |
| First project not created | +5 | In-app guided tour auto-launch |
| Team member not invited | +7 | "Invite your team" email with benefits |
| Integration not connected | +10 | Integration troubleshooting guide + offer call |
| No login in 7 days | +7 | "We noticed you haven't been back" re-engagement |
| No login in 14 days | +14 | CS manager outreach (manual) |