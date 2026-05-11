"""Marketplace pricing normalization primitives."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class MarketplaceProfile:
    """Configuration for marketplace-specific fee and tax behavior."""

    name: str
    fee_rate: float = 0.0
    fee_fixed: float = 0.0
    payment_processing_rate: float = 0.0
    payment_processing_fixed: float = 0.0
    tax_inclusive_pricing: bool = False
    default_shipping_cost: float = 0.0


@dataclass
class ListingInput:
    """Raw pricing inputs from a single listing/channel record."""

    sku: str
    channel: str
    listed_price: float
    shipping_charged: float = 0.0
    shipping_cost: Optional[float] = None
    tax_rate: float = 0.0
    explicit_fee: Optional[float] = None
    currency: str = "USD"
    assumptions: Dict[str, str] = field(default_factory=dict)


@dataclass
class NormalizedPricing:
    sku: str
    channel: str
    currency: str
    gross_revenue: float
    shipping_revenue: float
    net_sales_before_tax: float
    tax_amount: float
    marketplace_fee: float
    payment_processing_fee: float
    shipping_cost: float
    total_fees_and_costs: float


def normalize_pricing(listing: ListingInput, profile: MarketplaceProfile) -> NormalizedPricing:
    """Normalize listing economics into a channel-comparable structure."""

    shipping_cost = (
        listing.shipping_cost
        if listing.shipping_cost is not None
        else profile.default_shipping_cost
    )

    gross_revenue = listing.listed_price + listing.shipping_charged

    if profile.tax_inclusive_pricing:
        divisor = 1 + max(listing.tax_rate, 0)
        net_sales_before_tax = listing.listed_price / divisor if divisor else listing.listed_price
        tax_amount = listing.listed_price - net_sales_before_tax
    else:
        net_sales_before_tax = listing.listed_price
        tax_amount = listing.listed_price * max(listing.tax_rate, 0)

    marketplace_fee = (
        listing.explicit_fee
        if listing.explicit_fee is not None
        else (net_sales_before_tax * profile.fee_rate) + profile.fee_fixed
    )

    payment_processing_fee = (
        net_sales_before_tax * profile.payment_processing_rate
        + profile.payment_processing_fixed
    )

    total_fees_and_costs = marketplace_fee + payment_processing_fee + shipping_cost

    return NormalizedPricing(
        sku=listing.sku,
        channel=listing.channel,
        currency=listing.currency,
        gross_revenue=round(gross_revenue, 2),
        shipping_revenue=round(listing.shipping_charged, 2),
        net_sales_before_tax=round(net_sales_before_tax, 2),
        tax_amount=round(tax_amount, 2),
        marketplace_fee=round(marketplace_fee, 2),
        payment_processing_fee=round(payment_processing_fee, 2),
        shipping_cost=round(shipping_cost, 2),
        total_fees_and_costs=round(total_fees_and_costs, 2),
    )
