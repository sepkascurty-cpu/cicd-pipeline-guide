#!/usr/bin/env python3
"""pipeline.py — validate a CI/CD pipeline config before it runs.

Catches the boring-but-expensive mistakes: missing OIDC permissions,
deploy jobs without environments, production deploys without a strategy.

Usage:
    python pipeline.py pipeline.yaml
"""

import re
import sys


def load_yaml(path: str) -> dict:
    # Minimal YAML reader for workflow files — keys and simple scalars only.
    data, stack = {}, [(0, data)]
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.strip().partition(":")
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        node = {}
        stack[-1][1][key.strip()] = value if value else node
        if not value:
            stack.append((indent, node))
    return data


def validate(cfg: dict) -> list[str]:
    errors = []
    jobs = cfg.get("jobs", {})
    if not isinstance(jobs, dict):
        return ["top-level 'jobs' missing or malformed"]

    for name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        # 1. Deploy jobs must pin an environment (approvals, secrets scoping)
        if re.search(r"deploy|release", name, re.I):
            if "environment" not in job:
                errors.append(f"job '{name}': deploy job without 'environment' — "
                              "no approval gate or scoped secrets")
        # 2. OIDC: jobs touching the cloud need id-token: write, and must NOT
        #    also carry a long-lived credential secret
        steps = str(job.get("steps", ""))
        if "configure-aws-credentials" in steps or "azure/login" in steps:
            perms = str(cfg.get("permissions", "")) + str(job.get("permissions", ""))
            if "id-token" not in perms or "write" not in perms:
                errors.append(f"job '{name}': cloud login without OIDC "
                              "'id-token: write' permission")
            for blob in (str(cfg), str(job)):
                if re.search(r"AWS_SECRET|AZURE_CREDENTIALS|GCP_SA_KEY", blob):
                    errors.append(f"job '{name}': long-lived cloud key detected — "
                                  "use OIDC instead")
    # 3. Production deploys should name a strategy
    text = str(cfg)
    if re.search(r"production", text, re.I) and not re.search(
            r"blue.?green|canary|rolling|feature.?flag", text, re.I):
        errors.append("production deploy with no named strategy "
                      "(blue/green, canary, rolling, feature flag)")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: pipeline.py <workflow.yaml>")
        return 2
    cfg = load_yaml(sys.argv[1])
    errors = validate(cfg)
    if errors:
        print(f"✗ {len(errors)} problem(s) found:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("✓ pipeline config looks sane — ship it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
