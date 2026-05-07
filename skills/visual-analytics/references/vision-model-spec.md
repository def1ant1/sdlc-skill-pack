# Visual Analytics — Vision Model Specification

## Vision Task Taxonomy

| Task | Description | Model Approach | Output Format |
|------|-------------|---------------|--------------|
| `image_classification` | Classify image into predefined categories | CLIP / ViT | category + confidence |
| `object_detection` | Identify and locate objects with bounding boxes | YOLOv8 / RT-DETR | bounding_boxes + labels |
| `ocr` | Extract text from images | Tesseract / PaddleOCR | text + positions |
| `chart_analysis` | Parse charts and graphs to extract data | LLM with vision (Claude) | structured_data |
| `scene_understanding` | General description of image content | LLM with vision (Claude) | natural_language |
| `anomaly_detection` | Detect unusual patterns (infrastructure, security) | Autoencoder / CLIP | anomaly_score + regions |
| `document_layout` | Identify page structure (headers, tables, figures) | DocLayNet / LayoutLMv3 | layout_elements |
| `face_detection` | Detect (not identify) faces for privacy tagging | YOLOv8-face | face_regions |

---

## Visual Analysis Request Schema

```yaml
visual_analysis_request:
  request_id: "VIS-REQ-2026-xxxxx"
  image_uri: "gs://apotheon-images/screenshot-2026-05-07.png"
  mime_type: image/png

  tasks:
    - task: ocr
      config:
        language_hints: [en]
        detect_tables: true
    - task: chart_analysis
      config:
        extract_data_points: true
        output_format: structured_json
    - task: scene_understanding
      config:
        detail_level: high   # low | medium | high

  processing_options:
    rotate_if_needed: true
    enhance_contrast: false   # For low-quality images
    redact_faces: true         # Blur faces before any cloud processing

  output_format: unified   # unified | per_task
```

---

## Visual Analysis Output Schema

```yaml
visual_analysis_result:
  result_id: "VIS-RES-2026-xxxxx"
  request_id: "VIS-REQ-2026-xxxxx"
  processed_at: "2026-05-07T10:02:00Z"
  image_dimensions: {width: 1920, height: 1080}

  tasks:
    ocr:
      status: success
      text_blocks:
        - text: "Q2 Revenue: $12.4M"
          bounding_box: {x: 120, y: 240, w: 280, h: 32}
          confidence: 0.98

      tables_detected:
        - table_id: "VIS-TBL-001"
          bounding_box: {x: 100, y: 300, w: 800, h: 400}
          headers: [Metric, Q2 Actual, Q2 Target]
          rows:
            - [Revenue, "$12.4M", "$11.2M"]
            - [Gross Margin, "72%", "70%"]

    chart_analysis:
      status: success
      charts:
        - chart_id: "CHART-001"
          chart_type: bar | line | pie | scatter | table
          title: "Monthly Revenue Trend"
          data_series:
            - label: "Revenue"
              data_points:
                - {x: "Jan", y: 3800000}
                - {x: "Feb", y: 4100000}
                - {x: "Mar", y: 4500000}

    scene_understanding:
      status: success
      description: |
        A business presentation slide showing Q2 financial metrics. Contains a bar chart
        of monthly revenue trending upward, a summary table with Q2 actuals vs. targets,
        and text indicating revenue of $12.4M against an $11.2M target.
      objects_detected: [bar_chart, data_table, text_block, company_logo]
      dominant_colors: [navy_blue, white, green]
      faces_detected: 0

  processing_metadata:
    total_latency_ms: 1840
    models_used: [tesseract-5, claude-sonnet-4-6, paddleocr]
    faces_redacted: 0
```

---

## Model Selection Policy

```yaml
model_selection:
  rules:
    - if: "task == ocr AND image_type == printed_document"
      model: tesseract-5
      reason: "Fast, accurate for printed text"

    - if: "task == ocr AND image_type == handwritten"
      model: google-cloud-vision
      reason: "Better handwriting recognition"

    - if: "task == chart_analysis OR task == scene_understanding"
      model: claude-sonnet-4-6
      reason: "Multimodal LLM; best for semantic understanding"

    - if: "task == object_detection AND real_time_required == true"
      model: yolov8-nano
      reason: "Fastest inference; suitable for video stream"

    - if: "task == object_detection AND accuracy_priority == true"
      model: yolov8-x
      reason: "Highest accuracy"

    - if: "task == anomaly_detection"
      model: clip-vit-large-patch14
      reason: "Zero-shot anomaly detection via embedding distance"
```

---

## Privacy & Compliance Rules

```yaml
privacy_rules:
  face_handling:
    default_action: redact_before_processing   # Never send face images to cloud APIs
    blur_radius: 15
    exceptions: []   # No exceptions; always redact

  pii_in_images:
    detect: true    # Flag images containing text that looks like PII
    action_on_detection: classify_as_restricted

  data_retention:
    raw_images: 30_days
    extracted_features: 365_days
    analysis_results: 365_days

  cloud_processing:
    allowed_providers: [anthropic, google]
    must_redact_faces_before: true
    must_strip_exif: true
```

---

## Performance Targets

| Task | Image Size | Target Latency | GPU Required |
|------|-----------|---------------|-------------|
| OCR | 200 KB | < 2 s | No |
| Object detection (YOLOv8) | 1 MB | < 500 ms | Recommended |
| Chart analysis (Claude) | 500 KB | < 5 s | No (API call) |
| Scene understanding (Claude) | 1 MB | < 8 s | No (API call) |
| Anomaly detection (CLIP) | 500 KB | < 2 s | Recommended |
| Keyframe batch (100 frames) | 20 MB | < 60 s | Yes |