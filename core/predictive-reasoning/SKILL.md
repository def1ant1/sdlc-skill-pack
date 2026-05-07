---
name: predictive-reasoning
description: Applies temporal intelligence and predictive models to forecast enterprise outcomes including incidents, churn, infrastructure failures, and organizational trajectory across configurable time horizons.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [forecasting, knowledge-graph, simulation-engine, telemetry, data-fabric]
---

## Role

Predictive intelligence engine for the enterprise OS. Integrates telemetry signals, historical
patterns, and leading indicators to produce probabilistic forecasts of future enterprise states
— enabling proactive intervention before problems materialize as incidents, churn, or missed targets.

## Activation Triggers

- Weekly predictive intelligence cycle (automated)
- Anomalous leading indicator detected in telemetry
- Operator requests on-demand forecast for a specific domain
- Alert threshold approached requiring projection analysis
- Quarterly planning requiring forward-looking intelligence

## Execution Protocol

1. **Collect signals**: Aggregate telemetry metrics, operational KPIs, leading indicators,
   and external signals from data-fabric for the forecast domain.

2. **Select prediction models**: Match model type to forecast horizon and domain (short-term
   ARIMA for operational metrics, Prophet for seasonal trends, driver-based for revenue).

3. **Generate predictions**: Run models; produce point estimates with 80% and 95% confidence
   intervals; flag predictions with low confidence for additional scrutiny.

4. **Detect emerging risks**: Identify predictions that cross alert thresholds before they
   would trigger a reactive alert — proactive risk surfacing.

5. **Produce intelligence brief**: Ranked list of predicted outcomes with probability, impact,
   lead time available for intervention, and recommended proactive action.

6. **Update knowledge graph**: Persist predictions as forward-looking nodes; link to triggering
   signals; schedule accuracy assessment at prediction horizon.

## Output Format

Predictive intelligence brief with: top-10 predicted outcomes ranked by expected impact, P50/P80/P95
estimates, lead time for intervention, recommended actions, and model confidence grades.

## References

- `references/prediction-model-catalog.md` — model selection guide by forecast horizon and domain; leading indicator registry