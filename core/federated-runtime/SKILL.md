---
name: federated-runtime
description: Enables sovereign AI deployments across air-gapped, edge, and federated environments with distributed model synchronization, offline inference, and data residency compliance.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [local-runtime, distributed-agent-runtime, cluster-management, governance]
---

## Role

Sovereign and federated deployment runtime for the AI platform. Manages model distribution
to edge and air-gapped nodes, coordinates federated learning across sites without centralizing
sensitive data, enforces data residency constraints, and maintains synchronization between
federated deployments and the central OS.

## Activation Triggers

- Edge node deployment requested for a remote site
- Federated learning round initiated across multiple data-sovereign sites
- Air-gapped environment synchronization package prepared
- Data residency constraint enforcement required for cross-boundary workflow
- Federated node health check cycle

## Execution Protocol

1. **Register deployment target**: Classify node (cloud, on-prem, edge, air-gapped); record
   capabilities (GPU VRAM, connectivity, jurisdiction, compliance requirements).

2. **Package deployment artifact**: Select models and skills compatible with target constraints;
   bundle into a self-contained deployment package with all required dependencies.

3. **Distribute to target**: Push artifact via appropriate channel — API for connected nodes;
   encrypted offline bundle for air-gapped environments.

4. **Configure residency enforcement**: Apply data routing rules preventing prohibited cross-
   boundary data flows; configure audit logging for all cross-boundary transactions.

5. **Coordinate federated learning**: Aggregate model gradient updates from federated nodes
   using secure aggregation; update global model without exposing raw node data.

6. **Monitor federated health**: Heartbeat check all connected nodes; detect staleness (>24h
   without sync); trigger re-synchronization or alert operator for disconnected nodes.

## Output Format

Federated deployment status report with: node registry, sync status per node, residency
compliance check results, federated learning round summary, and offline package manifests.

## References

- `references/residency-enforcement-rules.md` — data residency constraints by jurisdiction, cross-boundary policy, federated sync protocol