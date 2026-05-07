# Reinforcement Optimizer — Algorithm Specifications

## Algorithm Selection Guide

| Algorithm | Best For | Requires Context? | Sample Efficiency | Convergence |
|-----------|---------|-------------------|-------------------|-------------|
| Epsilon-Greedy | Simple prompt variants; few arms | No | Low | Fast but suboptimal |
| UCB1 | Few arms; exploration needed | No | Medium | Theoretically optimal |
| Thompson Sampling | Many arms; Bayesian uncertainty | No | High | Good in practice |
| Contextual Bandit | Task-type dependent optimization | Yes | Medium | Depends on context richness |
| PPO | Sequential workflow optimization | Yes | Low | Slow but powerful |

**Default**: Thompson Sampling for prompt and config optimization; PPO for workflow optimization.

---

## Thompson Sampling Implementation

```python
import numpy as np
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ThompsonSamplingArm:
    """Beta distribution parameters for binary reward (success/failure)."""
    variant_id: str
    alpha: float = 1.0   # Successes + 1 (uniform prior)
    beta: float = 1.0    # Failures + 1

    @property
    def trials(self) -> int:
        return int(self.alpha + self.beta - 2)

    def sample(self) -> float:
        """Sample from Beta(alpha, beta) distribution."""
        return np.random.beta(self.alpha, self.beta)

    def update(self, reward: float, threshold: float = 0.7):
        """Update posterior with observed reward."""
        if reward >= threshold:
            self.alpha += 1.0  # Success
        else:
            self.beta += 1.0   # Failure


class ThompsonSamplingOptimizer:
    def __init__(self, target_id: str):
        self.target_id = target_id
        self.arms: Dict[str, ThompsonSamplingArm] = {}

    def register_variant(self, variant_id: str):
        self.arms[variant_id] = ThompsonSamplingArm(variant_id)

    def select_variant(self) -> str:
        """Select the variant with the highest sampled value."""
        samples = {vid: arm.sample() for vid, arm in self.arms.items()}
        return max(samples, key=samples.get)

    def update(self, variant_id: str, reward: float):
        self.arms[variant_id].update(reward)

    def is_converged(self, min_trials: int = 50, significance: float = 0.95) -> bool:
        """
        Check if the best variant is significantly better than the second best.
        Uses a simple probability of best arm being best.
        """
        if any(arm.trials < min_trials for arm in self.arms.values()):
            return False

        # Monte Carlo estimate of P(best arm is actually best)
        n_simulations = 10000
        win_counts = {vid: 0 for vid in self.arms}
        for _ in range(n_simulations):
            samples = {vid: arm.sample() for vid, arm in self.arms.items()}
            winner = max(samples, key=samples.get)
            win_counts[winner] += 1

        best_arm = max(win_counts, key=win_counts.get)
        return (win_counts[best_arm] / n_simulations) >= significance
```

---

## UCB1 Implementation

```python
import math

class UCB1Optimizer:
    def __init__(self, exploration_constant: float = 2.0):
        self.c = exploration_constant
        self.arms = {}
        self.total_trials = 0

    def select_variant(self) -> str:
        self.total_trials += 1
        # Force exploration: try each arm at least once
        for vid, arm in self.arms.items():
            if arm['trials'] == 0:
                return vid

        # UCB1 selection
        ucb_scores = {
            vid: arm['mean_reward'] + self.c * math.sqrt(
                math.log(self.total_trials) / arm['trials']
            )
            for vid, arm in self.arms.items()
        }
        return max(ucb_scores, key=ucb_scores.get)

    def update(self, variant_id: str, reward: float):
        arm = self.arms[variant_id]
        arm['trials'] += 1
        arm['mean_reward'] += (reward - arm['mean_reward']) / arm['trials']
```

---

## Reward Signal Taxonomy

| Reward Signal | Type | Range | Normalization |
|--------------|------|-------|---------------|
| `quality_score` | Float | [0, 1] | Already normalized |
| `latency_p95_ms` | Float | [0, ∞) | `1 - (latency / latency_budget)`, clipped to [0, 1] |
| `cost_per_run_usd` | Float | [0, ∞) | `1 - (cost / cost_budget)`, clipped to [0, 1] |
| `user_rating` | Integer | [1, 5] | `(rating - 1) / 4` → [0, 1] |
| `task_completion_rate` | Float | [0, 1] | Already normalized |
| `hitl_approval_rate` | Float | [0, 1] | Already normalized |

---

## Convergence Criteria

```yaml
convergence:
  thompson_sampling:
    min_trials_per_arm: 50
    probability_of_best_threshold: 0.95  # P(selected arm is best) >= 95%
    check_interval_trials: 10

  ucb1:
    min_trials_per_arm: 30
    confidence_interval_width_threshold: 0.05  # CI width < 5% → converged

  contextual_bandit:
    min_trials_total: 200
    policy_stability_window: 50  # Policy unchanged for 50 trials
    max_policy_change_threshold: 0.02

  # Global max duration (safety timeout)
  max_experiment_duration_days: 30

promotion:
  min_improvement_threshold: 0.05  # Winner must beat baseline by >= 5%
  requires_human_approval:
    - P0 skills
    - hitl-facing outputs
    - financial decision workflows
```

---

## Experiment Log Schema

```yaml
experiment:
  experiment_id: "RL-EXP-2026-xxxxx"
  target_id: "skill/code-review/system-prompt"
  target_type: prompt
  algorithm: thompson_sampling
  reward_signal: quality_score
  registered_at: "2026-05-07T00:00:00Z"
  status: running | converged | promoted | no_improvement | expired

  arms:
    - variant_id: "variant-A"
      description: "Baseline prompt"
      is_control: true
      trials: 147
      mean_reward: 0.791
      alpha: 118.0   # Thompson sampling
      beta: 30.0

    - variant_id: "variant-B"
      description: "Chain-of-thought variant with reasoning scaffolding"
      is_control: false
      trials: 153
      mean_reward: 0.847
      alpha: 131.0
      beta: 23.0

  convergence_check:
    last_checked_at: "2026-05-07T10:00:00Z"
    p_best_arm: 0.963   # Variant-B is best with 96.3% probability
    converged: true

  promotion:
    winner: "variant-B"
    improvement_pct: 7.1
    promoted_at: null
    promoted_by: null
```