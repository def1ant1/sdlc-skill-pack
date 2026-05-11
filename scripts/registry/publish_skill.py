#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--artifact", required=True)
    p.add_argument("--enable-public-publish", action="store_true")
    args = p.parse_args()

    if not args.enable_public_publish:
        print("public publish disabled by default; pass --enable-public-publish to opt in")
        return 0
    artifact = Path(args.artifact)
    if not artifact.exists():
        raise SystemExit(f"artifact does not exist: {artifact}")
    print(f"published artifact: {artifact}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
