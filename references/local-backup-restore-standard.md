# Local Backup/Restore Standard

## Scope
Applies to local runtime state and Docker stack metadata backups.

## Required controls
- Every backup MUST emit:
  - archive artifact
  - manifest metadata
  - sha256 checksums
- Restore MUST support `--dry-run` preview before live mutation.
- Secret-bearing paths are excluded by default.
- Secret restore/inclusion requires encrypted source + explicit operator approval ticket.

## Secret handling
- Use `--include-encrypted-secrets --approval-ticket <ID>` only after operator approval.
- Non-encrypted secrets (`.env`, plaintext secret files, tokens) remain excluded.

## Validation
- Post-restore checksum verification is required for restored files.
- Operators should run runtime health checks and workflow/schedule recovery drills after restore.
