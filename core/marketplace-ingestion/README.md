# Marketplace Ingestion

`core/marketplace-ingestion/` defines source adapters used to normalize data pulled from external marketplaces before entities are persisted.

## Source adapters

Adapters are lightweight translators that convert source-native payloads into canonical marketplace listing records while preserving lineage metadata.

* `source_adapters/base.py`: shared contract and record envelope.
* `source_adapters/ebay_adapter.py`: sample adapter for eBay style listing payloads.
* `source_adapters/amazon_adapter.py`: sample adapter for Amazon style listing payloads.
