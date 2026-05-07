---
name: reinforcement-optimizer
description: Applies multi-armed bandit and RL-based optimization to prompts, routing policies, and workflows using outcome feedback.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['cognitive-runtime', 'evolution-engine', 'telemetry']
---

## Role

Self-improving optimization engine for the Enterprise OS. Applies multi-armed bandit and
contextual RL algorithms to continuously improve prompts, model routing decisions, and
workflow configurations using outcome feedback collected from real executions. The platform
learns from its own operation and becomes measurably better over time.

## Activation Triggers

- A `prompt-optimization` experiment cycle is due (configured interval per prompt group)
- A `workflow-ab-testing` variant test has reached statistical significance threshold
- Outcome feedback is submitted for a previously optimized decision (online RL update)
- `evolution-engine` initiates a platform-wide optimization sweep
- Operator registers a new optimization target (new prompt, routing policy, or workflow)

## Execution Protocol

1. **Register optimization target**: Accept a target definition:
   - `target_type`: `prompt` | `routing_policy` | `workflow_config`
   - `target_id`: unique identifier
   - `action_space`: list of variants or parameter ranges to optimize over
   - `reward_signal`: which outcome metric to maximize (quality score, latency, cost, user rating)
   - `algorithm`: `epsilon_greedy` | `ucb1` | `thompson_sampling` | `contextual_bandit` | `ppo`

2. **Variant selection**: On each trial, select the next action using the chosen algorithm:
   - Epsilon-greedy / UCB1 / Thompson Sampling: for stateless prompt/config choices
   - Contextual bandit: when context features (task type, user segment, time) should influence selection
   - PPO: for sequential workflow optimization where actions have dependencies

3. **Execute trial**: Invoke the selected variant via the appropriate runtime
   (`sdlc-orchestration` for prompts, `workflow-runtime` for workflows).

4. **Collect reward**: After execution completes, collect the reward signal:
   - Quality metrics from skill output evaluation
   - Latency and cost from telemetry
   - Human feedback scores from `hitl-dashboard` (when available)

5. **Update model**: Apply the RL update to the algorithm's internal model:
   - Update Q-values / posterior distribution / policy gradient
   - Record trial result in the experiment log

6. **Convergence check**: After N trials, test for statistical significance.
   If the best variant is significantly better (p < 0.05, effect size > threshold), promote it
   as the default and archive the experiment. Notify the registered owner.

## Output Format

```yaml
rl_optimizer:
  target_id: "prompt/code-review-system-prompt"
  algorithm: thompson_sampling
  trial_count: 147
  current_best_variant: "variant-B"
  current_best_reward: 0.847
  baseline_reward: 0.791
  improvement_pct: 7.1
  status: running | converged | promoted
  promoted_at: null  # ISO timestamp when promoted to default
```

## References

- `references/` — Algorithm specifications, convergence criteria, reward signal taxonomy, experiment log schema
