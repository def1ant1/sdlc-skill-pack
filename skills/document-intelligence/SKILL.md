---
name: document-intelligence
description: Extracts structure from PDF, Word, and Excel files including tables, contracts, and OCR text for enterprise multi-modal processing.
metadata:
  version: "0.1.0"
  category: multimodal
  owner: platform
  maturity: draft
  dependencies: ['multimodal-runtime']
---

## Role

Enterprise document understanding skill. Extracts structured information from unstructured
or semi-structured business documents: PDFs, Word files, Excel spreadsheets, and scanned
images. Outputs structured representations that downstream agents and skills can query
and reason over without reading raw documents.

## Activation Triggers

- `multimodal-runtime` routes a document-type input for processing
- A contract or policy document is ingested and requires clause extraction
- A financial report (PDF/Excel) requires table extraction for analytics
- An operator submits a document for intelligence extraction
- `enterprise-integration-hub` receives a document attachment from an enterprise system

## Execution Protocol

1. **Format detection**: Identify document format (PDF, DOCX, XLSX, image-PDF, native-PDF).
   For image-PDFs (scanned documents), route through OCR pipeline first.

2. **OCR** (for image-PDFs and scanned documents):
   - Apply multi-language OCR
   - Compute confidence score per page
   - Flag pages with confidence < 0.85 for human review

3. **Structure extraction**:
   - **Layout analysis**: identify headers, paragraphs, tables, figures, footers
   - **Table extraction**: parse table headers and rows into structured JSON arrays
   - **Section detection**: identify document sections and their hierarchy
   - **Key-value extraction**: identify form fields, labels, and values

4. **Named entity recognition**: Extract:
   - Dates, monetary amounts, percentages
   - Organization names, person names, addresses
   - Contract-specific: parties, effective date, term, obligation clauses

5. **Document classification**: Classify document type:
   `contract` | `invoice` | `report` | `policy` | `form` | `presentation` | `specification`

6. **Output assembly**: Return structured document intelligence for downstream consumption.

## Output Format

```yaml
document_intelligence:
  document_id: "DOC-2026-xxxxx"
  format: pdf | docx | xlsx
  page_count: 0
  document_type: contract
  ocr_applied: false
  ocr_confidence_min: null
  sections: []
  tables: []
  entities:
    dates: []
    organizations: []
    amounts: []
  key_values: {}
  requires_human_review: false
```

## Quality Gates

- OCR confidence < 0.85 on any page → flag for human review (do not return as high-confidence)
- Table extraction must preserve header-row association (no floating cell values)

## References

- `references/` — Supported format matrix, entity extraction schema, document classification taxonomy
