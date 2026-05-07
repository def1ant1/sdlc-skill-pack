# Document Intelligence — Extraction Schema & Processing Specification

## Supported Document Types

| Format | MIME Type | Extraction Method | OCR Required |
|--------|-----------|------------------|-------------|
| PDF (native text) | application/pdf | Direct text extraction | No |
| PDF (scanned) | application/pdf | OCR (Tesseract / Google Vision) | Yes |
| DOCX | application/vnd.openxmlformats... | python-docx | No |
| XLSX / XLS | application/vnd.ms-excel | openpyxl | No |
| PPTX | application/vnd.ms-powerpoint | python-pptx | No |
| TXT / Markdown | text/plain, text/markdown | Direct read | No |
| PNG / JPG (document scan) | image/png, image/jpeg | OCR | Yes |
| TIFF | image/tiff | OCR | Yes |

---

## Extraction Output Schema

```yaml
document_extract:
  extract_id: "DOC-EXT-2026-xxxxx"
  source_uri: "gs://enterprise-os-docs/Q2-board-deck.pdf"
  extracted_at: "2026-05-07T10:05:00Z"
  extraction_version: "1.0"

  metadata:
    title: "Q2 2026 Board Deck"
    author: "Finance Team"
    created_at: "2026-05-01T00:00:00Z"
    page_count: 24
    word_count: 4820
    language: en
    ocr_applied: false
    ocr_confidence_mean: null

  # Full text content, page-segmented
  pages:
    - page_number: 1
      text: |
        Q2 2026 Board Review
        Enterprise OS Division
        May 7, 2026
      tables: []
      images: []

    - page_number: 4
      text: |
        Q2 Financial Performance
        Revenue: $12.4M vs $11.2M target
      tables:
        - table_id: "tbl-p4-001"
          caption: "Q2 Financial Summary"
          headers: [Metric, Q2 Actual, Q2 Target, Variance]
          rows:
            - [Revenue, "$12.4M", "$11.2M", "+10.7%"]
            - [Gross Margin, "72%", "70%", "+2pp"]
      images: []

  # Extracted structured elements
  tables:
    - table_id: "tbl-p4-001"
      page: 4
      data_type: financial_metrics
      row_count: 6
      col_count: 4

  # Named entities across full document
  entities:
    organizations: ["Enterprise OS Inc", "Acme Corp"]
    people: ["Alice Chen", "Bob Smith"]
    dates: ["2026-05-07", "2026-06-30", "2026-Q2"]
    amounts: ["$12.4M", "$11.2M", "72%"]
    locations: ["San Francisco"]

  # Key-value pairs extracted from forms / structured pages
  key_value_pairs:
    - key: "Total Revenue"
      value: "$12.4M"
      page: 4
      confidence: 0.97

  # Action items extracted (if meeting notes / board minutes)
  action_items:
    - text: "Alice to deliver SOC2 evidence package by May 14"
      assignee: "Alice Chen"
      due_date: "2026-05-14"
      page: 12
      confidence: 0.91

  # Summary (LLM-generated)
  summary: |
    Q2 board deck covering financial performance (revenue +10.7% vs. target),
    product roadmap for waves 9–13, and compliance status. Key decisions:
    approve wave-9 go-live, authorize $250K for DR infrastructure upgrade.

  # Data governance
  data_classification: CONFIDENTIAL   # Auto-classified based on content
  contains_pii: true
  pii_types: [person_names, financial_data]
```

---

## Processing Pipeline

```
Document received (URI or binary)
        │
        ▼
1. MIME type detection (libmagic)
        │
        ▼
2. Pre-processing
   ├── PDF: check if text-layer present (pdfminer)
   ├── If scanned PDF or image: OCR (Tesseract or cloud OCR)
   └── Office formats: extract via python-docx/openpyxl
        │
        ▼
3. Text extraction (page-segmented)
        │
        ▼
4. Table extraction
   ├── PDF: pdfplumber
   └── XLSX: openpyxl direct
        │
        ▼
5. Named Entity Recognition (spaCy + custom rules)
        │
        ▼
6. Key-value pair extraction (for forms)
        │
        ▼
7. Action item extraction (LLM call, structured output)
        │
        ▼
8. LLM summarization (claude-haiku for speed)
        │
        ▼
9. Data classification (rule-based + LLM assist)
        │
        ▼
10. Assemble extraction record → return to caller
```

---

## OCR Quality Thresholds

| Condition | Action |
|-----------|--------|
| Mean confidence ≥ 0.90 | Accept; proceed with extraction |
| Mean confidence 0.70–0.89 | Accept with `ocr_quality: degraded` flag; notify caller |
| Mean confidence < 0.70 | Reject; return `EXTRACTION_FAILED` with reason |
| Any page confidence < 0.60 | Flag that page; exclude from entity extraction |

---

## Extraction Performance Targets

| Document Type | Size | Target Latency |
|--------------|------|---------------|
| PDF, 10 pages, no OCR | ~500 KB | < 15 s |
| PDF, 100 pages, no OCR | ~5 MB | < 90 s |
| PDF, 10 pages, with OCR | ~2 MB | < 60 s |
| XLSX, 10,000 rows | ~1 MB | < 10 s |
| DOCX, 50 pages | ~500 KB | < 20 s |

Latency measured from receipt of document URI to return of complete extraction record.