# Local Backup/Restore Standard

## Scope
This standard defines local operational backup and restore expectations for:
- Runtime `runs/`, `artifacts/`, and `reports/`
- Schedule run outputs
- Qdrant local storage
- Local app volumes
- PostgreSQL logical dumps (when DB access is configured)
- Configuration snapshots with secret exclusion by default

## Backup Requirements
1. Produce a backup directory containing all collected assets.
2. Produce `manifest.json` documenting:
   - UTC creation timestamp
   - included/excluded content
   - policy posture for secret handling
3. Produce `checksums.sha256` for all backed-up files except the manifest/checksum files.
4. Bundle as `.tar.gz` for transfer and archival.

## Secret Protection
- Secret material MUST be excluded by default.
- Secret material MAY be included only when all conditions are true:
  1. Operator passes explicit approval artifact/ticket.
  2. Backup operation is flagged as encrypted.
  3. Inclusion is intentionally requested.
- If these conditions are not met, backup MUST fail closed or skip secret-like paths.

## Restore Requirements
1. Verify checksums before applying any changes.
2. Support `--dry-run` mode that previews each planned restore action.
3. Abort restore if integrity checks fail.
4. Restore from either unpacked backup directories or `.tar.gz` archives.
