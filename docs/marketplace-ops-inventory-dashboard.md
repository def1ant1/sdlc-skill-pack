# Marketplace Ops, Inventory, and Dashboard Documentation

## Overview
This document summarizes ecommerce extension capabilities spanning listing operations, inventory/catalog intelligence, and dashboard analytics.

## Listing Operations
All listing operation skills run in `draft` mode by default and require publish approval gates before marketplace mutations.

## Catalog and Inventory
Catalog normalization plus inventory intelligence skills preserve canonical SKU and marketplace segmentation and emit required metrics where applicable.

## Dashboard and Reports
`apps/ecommerce-dashboard/` and ecommerce reports expose required metrics:
- gross_margin
- net_margin
- sell_through
- aging_days
- return_rate
- shipping_fee_ratio
- conversion_rate
- cac

All views must support marketplace and SKU segmentation.
