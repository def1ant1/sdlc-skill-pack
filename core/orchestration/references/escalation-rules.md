# Escalation Rules

Escalate to governance review when:

- personal data is processed
- AI model behavior affects users materially
- financial, legal, health, employment, or safety outcomes are involved
- deployment changes production infrastructure
- secrets, credentials, permissions, or auth are changed
- an architectural decision introduces vendor lock-in or high operational risk

Escalate to architecture review when:

- new service boundaries are proposed
- data models change
- API contracts change
- scalability or reliability assumptions change
- integration patterns change
