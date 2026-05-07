# Lineage Graph Schema Reference

## Graph Data Model

### Node Types

```yaml
node_types:
  - type: "dataset"
    properties:
      id: string  # Unique identifier
      name: string
      location: string  # URI or table path
      schema_version: string
      record_count: integer
      created_at: timestamp
      last_updated: timestamp
      owner: string
      tags: list[string]
      pii_classification: "L1" | "L2" | "L3" | "L4" | "none"

  - type: "pipeline"
    properties:
      id: string
      name: string
      pipeline_type: "batch" | "streaming" | "transformation" | "ml_training"
      schedule: string  # cron expression or "streaming"
      owner: string
      git_ref: string  # Git commit/tag of pipeline code
      sla_minutes: integer

  - type: "model"
    properties:
      id: string
      name: string
      version: string
      framework: string
      training_dataset_id: string
      trained_at: timestamp
      registry_uri: string

  - type: "report"
    properties:
      id: string
      name: string
      report_type: "dashboard" | "export" | "aggregate" | "audit"
      consumer: string
      schedule: string

  - type: "column"
    properties:
      id: string
      parent_dataset_id: string
      name: string
      data_type: string
      pii_classification: "L1" | "L2" | "L3" | "L4" | "none"
```

### Edge Types

```yaml
edge_types:
  - type: "READS_FROM"
    description: "Pipeline reads from dataset"
    from_types: [pipeline]
    to_types: [dataset]
    properties:
      columns_read: list[string]  # Specific columns, or "*" for all
      filter_applied: string  # SQL WHERE clause if applicable

  - type: "WRITES_TO"
    description: "Pipeline writes to dataset"
    from_types: [pipeline]
    to_types: [dataset]
    properties:
      write_mode: "append" | "overwrite" | "upsert" | "merge"
      partition_key: string

  - type: "TRAINED_ON"
    description: "Model trained using dataset"
    from_types: [model]
    to_types: [dataset]
    properties:
      split: "full" | "train" | "validation" | "test"
      feature_columns: list[string]
      label_column: string

  - type: "DERIVED_FROM"
    description: "Column-level lineage: column derived from other columns"
    from_types: [column]
    to_types: [column]
    properties:
      transformation: string  # SQL expression or description
      confidence: float  # 0.0-1.0 (1.0 = exact lineage; < 1.0 = inferred)

  - type: "CONSUMED_BY"
    description: "Dataset consumed by a report or external system"
    from_types: [dataset]
    to_types: [report]
```

---

## Lineage Graph Serialization (JSON-LD)

```json
{
  "@context": "https://apotheon.io/lineage/v1",
  "@type": "LineageGraph",
  "graph_id": "LG-20260507-001",
  "captured_at": "2026-05-07T12:00:00Z",
  "nodes": [
    {
      "@id": "ds:raw_events_2026",
      "@type": "dataset",
      "name": "Raw Events Log — 2026",
      "location": "s3://data-lake/raw/events/2026/",
      "owner": "data-engineering",
      "pii_classification": "L2"
    },
    {
      "@id": "pl:event_aggregation_pipeline",
      "@type": "pipeline",
      "name": "Event Aggregation Pipeline",
      "pipeline_type": "batch",
      "schedule": "0 2 * * *",
      "git_ref": "v2.3.1"
    },
    {
      "@id": "ds:daily_event_summary",
      "@type": "dataset",
      "name": "Daily Event Summary",
      "location": "s3://data-lake/processed/event_summary/",
      "pii_classification": "none"
    }
  ],
  "edges": [
    {
      "@type": "READS_FROM",
      "from": "pl:event_aggregation_pipeline",
      "to": "ds:raw_events_2026",
      "columns_read": ["event_type", "user_id", "timestamp", "value"],
      "filter_applied": "WHERE date = current_date - 1"
    },
    {
      "@type": "WRITES_TO",
      "from": "pl:event_aggregation_pipeline",
      "to": "ds:daily_event_summary",
      "write_mode": "append",
      "partition_key": "date"
    }
  ]
}
```

---

## Lineage Traversal Queries

### Upstream Lineage (What does this dataset depend on?)

```
FUNCTION upstream_lineage(dataset_id, max_hops=10):
    visited = {dataset_id}
    frontier = [dataset_id]
    upstream = []

    FOR hop IN 1..max_hops:
        next_frontier = []
        FOR node IN frontier:
            # Find all READS_FROM edges pointing TO this dataset
            # i.e., pipelines that read this dataset
            pipelines = graph.predecessors(node, edge_type=WRITES_TO)
            FOR pipeline IN pipelines:
                sources = graph.predecessors(pipeline, edge_type=READS_FROM)
                FOR source IN sources:
                    IF source NOT IN visited:
                        visited.add(source)
                        next_frontier.append(source)
                        upstream.append({node: source, hop: hop})
        frontier = next_frontier
        IF NOT frontier: BREAK

    RETURN upstream
```

### Downstream Impact (What will break if this dataset changes?)

```
FUNCTION downstream_impact(dataset_id, max_hops=10):
    visited = {dataset_id}
    impacted = []
    frontier = [dataset_id]

    FOR hop IN 1..max_hops:
        next_frontier = []
        FOR node IN frontier:
            # Pipelines that read this dataset
            pipelines = graph.successors(node, edge_type=READS_FROM)
            FOR pipeline IN pipelines:
                # What datasets does this pipeline write to
                outputs = graph.successors(pipeline, edge_type=WRITES_TO)
                FOR output IN outputs:
                    IF output NOT IN visited:
                        visited.add(output)
                        next_frontier.append(output)
                        impacted.append({source: node, affected: output, hop: hop})
        frontier = next_frontier
        IF NOT frontier: BREAK

    RETURN impacted
```

---

## PII Propagation Tracking

```
RULE: PII classification of output ≥ max(PII classification of inputs)
  L4 < L3 < L2 < L1 (L1 is most sensitive)

EXCEPTION: Explicit de-identification applied (verified by data-redaction skill)
  THEN: output_classification = "none" (must be verified, not assumed)

pii_propagation_check(pipeline):
  FOR each output_dataset d_out:
    input_classifications = [d_in.pii_classification FOR d_in IN pipeline.inputs]
    expected_output_classification = max(input_classifications)
    IF d_out.pii_classification < expected_output_classification:
      IF NOT pipeline.has_verified_deidentification:
        RAISE PII_PROPAGATION_VIOLATION(pipeline, d_out)
```