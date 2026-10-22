#!/usr/bin/env python3
"""Stop hook: apply <!-- naksha-memory-update {...} --> blocks to .naksha/project.json.

Deterministic replacement for the model-judged prompt hook. Always exits 0 and
prints nothing, so a session with no blocks (the usual case) ends cleanly.
"""
import datetime
import json
import os
import re
import sys

BLOCK = re.compile(r"<!--\s*naksha-memory-update\s*(\{.*?\})\s*-->", re.S)


def log_error(project, msg):
    try:
        d = os.path.expanduser("~/.naksha")
        os.makedirs(d, exist_ok=True)
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(os.path.join(d, "hook-errors.log"), "a") as f:
            f.write(f"[{ts}] [{project or 'unknown'}] {msg}\n")
    except OSError:
        pass


def strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for x in node:
            yield from strings(x)
    elif isinstance(node, dict):
        for x in node.values():
            yield from strings(x)


def find_project(start):
    d = os.path.abspath(start)
    for _ in range(4):
        p = os.path.join(d, ".naksha", "project.json")
        if os.path.isfile(p):
            return p
        d = os.path.dirname(d)
    return None


def set_path(obj, path, value):
    keys = path.split(".")
    for k in keys[:-1]:
        if not isinstance(obj.get(k), dict):
            obj[k] = {}
        obj = obj[k]
    obj[keys[-1]] = value


def main():
    try:
        hook = json.load(sys.stdin)
    except Exception:
        return
    tp = hook.get("transcript_path")
    if not tp or not os.path.isfile(tp):
        return
    payloads = []
    with open(tp, errors="replace") as f:
        for line in f:
            if "naksha-memory-update" not in line:
                continue
            try:
                text = "\n".join(strings(json.loads(line)))
            except Exception:
                continue
            for m in BLOCK.finditer(text):
                try:
                    p = json.loads(m.group(1))
                except Exception:
                    continue  # documentation placeholders like {"type": "...", ...}
                if isinstance(p, dict) and p.get("type") in ("project_json_patch", "browser_finding_write"):
                    payloads.append(p)
    if not payloads:
        return
    pj = find_project(hook.get("cwd") or os.getcwd())
    if not pj:
        log_error(None, f"{len(payloads)} memory update(s) found but .naksha/project.json not found from {hook.get('cwd')}")
        return
    try:
        with open(pj) as f:
            data = json.load(f)
        for p in payloads:
            if p["type"] == "project_json_patch" and p.get("path"):
                set_path(data, p["path"], p.get("value"))
            elif p["type"] == "browser_finding_write" and "finding" in p:
                arr = data.get("browser_findings")
                arr = arr if isinstance(arr, list) else []
                if p["finding"] not in arr:  # Stop fires every turn; don't re-add
                    arr.insert(0, p["finding"])
                data["browser_findings"] = arr[:20]
        tmp = pj + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, pj)
    except Exception as e:
        log_error(pj, f"failed to apply memory updates: {e}")


try:
    main()
except Exception:
    pass
sys.exit(0)
