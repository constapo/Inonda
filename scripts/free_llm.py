#!/usr/bin/env python3
"""Delegate a prompt to free-tier LLM APIs from the command line (stdlib only).

Every provider below speaks the OpenAI-compatible /chat/completions protocol.
API keys are read from the environment and never printed:

    OPENROUTER_API_KEY   https://openrouter.ai/keys        (models ending in ":free")
    GROQ_API_KEY         https://console.groq.com/keys
    GEMINI_API_KEY       https://aistudio.google.com/apikey
    CEREBRAS_API_KEY     https://cloud.cerebras.ai/

Model names change often, so none are hard-coded. Discover them, then pick one:

    python3 free_llm.py list --provider groq
    python3 free_llm.py ask  --provider groq --model <id> "Summarise this diff: ..."
    GROQ_MODEL=<id> GEMINI_MODEL=<id> python3 free_llm.py ask --provider all "question"

`--provider all` queries every provider that has both a key and a <PROVIDER>_MODEL
env var, in parallel, and prints each answer under its own heading.

Privacy: whatever you send goes to a third party, and free tiers may log or train
on it. Do not send secrets, credentials or customer data.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

PROVIDERS = {
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
    "cerebras": ("https://api.cerebras.ai/v1", "CEREBRAS_API_KEY"),
}
TIMEOUT = 120


def _call(provider, path, payload=None):
    base, key_env = PROVIDERS[provider]
    key = os.environ.get(key_env, "").strip()
    if not key:
        raise RuntimeError(f"{key_env} is not set")
    req = urllib.request.Request(
        base + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        # Status and provider message only; the request (and key) is never echoed.
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"network error: {e.reason}") from None


def list_models(provider):
    data = _call(provider, "/models").get("data", [])
    return sorted(m.get("id", "") for m in data if m.get("id"))


def ask(provider, model, prompt, system=None):
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    out = _call(provider, "/chat/completions", {"model": model, "messages": messages})
    return out["choices"][0]["message"]["content"]


def read_prompt(arg):
    return sys.stdin.read() if arg in (None, "-") else arg


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list", help="list model ids a provider offers to your key")
    ls.add_argument("--provider", required=True, choices=sorted(PROVIDERS))
    aq = sub.add_parser("ask", help="send a prompt (use '-' or omit to read stdin)")
    aq.add_argument("--provider", required=True, choices=sorted(PROVIDERS) + ["all"])
    aq.add_argument("--model", help="model id (or set <PROVIDER>_MODEL)")
    aq.add_argument("--system", help="optional system prompt")
    aq.add_argument("prompt", nargs="?")
    args = p.parse_args()

    try:
        if args.cmd == "list":
            print("\n".join(list_models(args.provider)))
            return 0

        prompt = read_prompt(args.prompt)
        if args.provider != "all":
            model = args.model or os.environ.get(args.provider.upper() + "_MODEL")
            if not model:
                p.error(f"--model or {args.provider.upper()}_MODEL is required")
            print(ask(args.provider, model, prompt, args.system))
            return 0

        jobs = {
            name: os.environ[name.upper() + "_MODEL"]
            for name, (_, key_env) in PROVIDERS.items()
            if os.environ.get(key_env) and os.environ.get(name.upper() + "_MODEL")
        }
        if not jobs:
            p.error("no provider has both an API key and a <PROVIDER>_MODEL env var")

        def run(item):
            name, model = item
            try:
                return name, model, ask(name, model, prompt, args.system)
            except Exception as e:  # report per-provider failures without hiding the others
                return name, model, f"[error] {e}"

        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            for name, model, text in pool.map(run, jobs.items()):
                print(f"## {name} ({model})\n{text}\n")
        return 0
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
