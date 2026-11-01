#!/usr/bin/env python3
"""Print an unsigned dev JWT (sub=local-dev-user). The API accepts these outside production only."""
import base64
import json
import sys


def enc(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")


print(f"{enc({'alg': 'none'})}.{enc({'sub': sys.argv[1] if len(sys.argv) > 1 else 'local-dev-user'})}.x")
