# Workflow Router

## Primary Intent Detection

| User Intent | Classification | First Skill |
|---|---|---|
| build a feature | delivery workflow | sdlc-orchestration |
| write requirements | product workflow | requirements-engineering |
| design system | architecture workflow | system-architecture |
| review code or design | review workflow | code-review |
| make secure | security workflow | devsecops |
| write tests | QA workflow | qa-automation |
| deploy or release | release workflow | release-management |
| investigate incident | operations workflow | sre-incident-response |
| summarize status | leadership workflow | executive-reporting |

## Escalate To Orchestration When

- more than one SDLC phase is involved
- multiple artifacts are required
- architecture, implementation, and testing are all mentioned
- the task involves AI governance or compliance
- the user asks for an end-to-end plan
