"""Profitability and confidence scoring for normalized marketplace pricing."""

from dataclasses import dataclass

from .normalization import NormalizedPricing


@dataclass
class ProfitabilityOutput:
    sku: str
    channel: str
    currency: str
    cogs: float
    net_profit: float
    net_margin: float
    confidence_score: float


def compute_confidence_score(*, used_default_shipping: bool, explicit_fee_provided: bool, tax_rate_provided: bool) -> float:
    """Return confidence score from 0 to 1 based on input completeness."""

    score = 1.0
    if used_default_shipping:
        score -= 0.2
    if not explicit_fee_provided:
        score -= 0.1
    if not tax_rate_provided:
        score -= 0.1
    return max(0.0, round(score, 2))


def compute_profitability(
    normalized: NormalizedPricing,
    *,
    cogs: float,
    used_default_shipping: bool,
    explicit_fee_provided: bool,
    tax_rate_provided: bool,
) -> ProfitabilityOutput:
    """Calculate profit and net margin using normalized channel economics."""

    net_profit = normalized.net_sales_before_tax - normalized.total_fees_and_costs - cogs
    net_margin = (net_profit / normalized.net_sales_before_tax) if normalized.net_sales_before_tax else 0.0

    confidence_score = compute_confidence_score(
        used_default_shipping=used_default_shipping,
        explicit_fee_provided=explicit_fee_provided,
        tax_rate_provided=tax_rate_provided,
    )

    return ProfitabilityOutput(
        sku=normalized.sku,
        channel=normalized.channel,
        currency=normalized.currency,
        cogs=round(cogs, 2),
        net_profit=round(net_profit, 2),
        net_margin=round(net_margin, 4),
        confidence_score=confidence_score,
    )
