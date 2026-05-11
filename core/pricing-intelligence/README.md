# Pricing Intelligence Core

The `core/pricing-intelligence/` module provides shared normalization and profitability primitives for marketplace pricing workflows.

## Capabilities
- Normalize listing prices, shipping, taxes, and fees across marketplaces.
- Apply profile-level defaults and overrides for fee policies.
- Produce channel-level and SKU-level profitability summaries.
- Emit confidence scores based on field completeness and assumptions.

## Core Components
- `normalization.py`: fee and tax normalization engine.
- `profitability.py`: net margin and confidence scoring outputs.
