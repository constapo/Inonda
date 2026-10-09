#!/usr/bin/env python3
"""Index installed Claude agents, skills and free-LLM providers by capability.

Reads ~/.claude/agents/*.md and ~/.claude/skills/*/SKILL.md (frontmatter only),
scores each against capability domains, and writes:

    ~/.claude/agent-index.md     human-readable routing table
    ~/.claude/agent-index.json   same data for tooling

Within a domain, agents are ranked by (keyword score, number of matching skills,
tool breadth). "Heavy workload" routing = take the top agents of the domain.

    python3 build_agent_index.py [--home DIR] [--top N]

Stdlib only. Never prints environment values, only whether a key is set.
"""
import argparse
import json
import os
import re
from pathlib import Path

# domain -> keywords. Name hits weigh 3x description hits.
DOMAINS = {
    "security": ["security", "pentest", "vulnerab", "threat", "owasp", "crypto", "audit", "compliance", "secrets"],
    "frontend": ["frontend", "react", "vue", "angular", "svelte", "css", "tailwind", "nextjs", "ui component", "accessibility"],
    "backend": ["backend", "api", "rest", "graphql", "microservice", "django", "fastapi", "express", "spring", "node"],
    "database-data": ["database", "sql", "postgres", "mysql", "mongodb", "redis", "schema", "migration", "etl", "warehouse"],
    "ml-ai": ["machine learning", "llm", "rag", "prompt", "embedding", "mlops", "neural", "model training", "ai engineer"],
    "devops-cloud": ["devops", "kubernetes", "docker", "terraform", "aws", "azure", "gcp", "ci/cd", "deploy", "sre", "infrastructure"],
    "testing-qa": ["test", "qa", "e2e", "playwright", "jest", "pytest", "coverage", "tdd"],
    "code-quality": ["review", "refactor", "lint", "clean code", "debug", "performance", "optimi"],
    "architecture-planning": ["architect", "design pattern", "system design", "planning", "roadmap", "spec", "requirements"],
    "languages": ["python", "typescript", "javascript", "golang", "rust", "java", "kotlin", "swift", "csharp", "php", "ruby", "cpp"],
    "mobile": ["mobile", "ios", "android", "flutter", "react native", "swiftui"],
    "docs-writing": ["documentation", "technical writ", "readme", "changelog", "copywrit", "blog", "content"],
    "marketing-seo": ["marketing", "seo", "campaign", "ads", "growth", "email sequence", "social media", "analytics"],
    "design-ux": ["design", "ux", "figma", "brand", "visual", "wireframe", "illustration"],
    "science-research": ["research", "scientific", "bioinformatics", "chemistry", "genomic", "literature", "statistic", "paper"],
    "product-business": ["product manager", "business", "finance", "legal", "sales", "customer", "hr", "project manage"],
}


def frontmatter(path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            k, sep, v = line.partition(":")
            if sep and k.strip() in ("name", "description", "tools"):
                out[k.strip()] = v.strip().strip("\"'")
    return out


def load(home):
    agents, skills = [], []
    for f in sorted((home / "agents").glob("*.md")):
        fm = frontmatter(f)
        tools = [t.strip() for t in fm.get("tools", "").split(",") if t.strip()]
        agents.append({"id": f.stem, "desc": fm.get("description", "")[:240], "tools": tools})
    for f in sorted((home / "skills").glob("*/SKILL.md")):
        fm = frontmatter(f)
        skills.append({"id": f.parent.name, "desc": fm.get("description", "")[:240]})
    return agents, skills


def score(item, words):
    name = item["id"].lower().replace("-", " ").replace("_", " ")
    desc = item["desc"].lower()
    return sum(3 for w in words if w in name) + sum(1 for w in words if w in desc)


def build(agents, skills, top):
    skill_by_domain = {
        d: sorted((s for s in skills if score(s, w) > 0), key=lambda s: -score(s, w))
        for d, w in DOMAINS.items()
    }
    index = {}
    for d, words in DOMAINS.items():
        ranked = []
        for a in agents:
            sc = score(a, words)
            if sc:
                ranked.append((sc, len(skill_by_domain[d]), len(a["tools"]), a["id"]))
        ranked.sort(reverse=True)
        index[d] = {
            "agents": [r[3] for r in ranked[:top]],
            "agent_count": len(ranked),
            "skills": [s["id"] for s in skill_by_domain[d][:top]],
            "skill_count": len(skill_by_domain[d]),
        }
    return index


def providers():
    table = {
        "openrouter": "OPENROUTER_API_KEY",
        "groq": "GROQ_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "cerebras": "CEREBRAS_API_KEY",
    }
    return {
        p: {"key_set": bool(os.environ.get(k)), "model_set": bool(os.environ.get(p.upper() + "_MODEL"))}
        for p, k in table.items()
    }


def render(index, n_agents, n_skills, prov):
    lines = [
        "# Agent / skill / free-LLM routing index",
        f"\n{n_agents} agents, {n_skills} skills scanned. Pick a domain, delegate to its top agents.\n",
        "| domain | agents matched | skills matched | top agents | top skills |",
        "|---|---|---|---|---|",
    ]
    for d, v in sorted(index.items(), key=lambda kv: -kv[1]["agent_count"]):
        lines.append(
            f"| {d} | {v['agent_count']} | {v['skill_count']} | "
            f"{', '.join(v['agents'])} | {', '.join(v['skills'])} |"
        )
    lines += ["\n## Free-LLM providers (scripts/free_llm.py)\n", "| provider | key | model env |", "|---|---|---|"]
    for p, v in prov.items():
        lines.append(f"| {p} | {'set' if v['key_set'] else 'missing'} | {'set' if v['model_set'] else 'missing'} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--home", default=str(Path.home() / ".claude"), help="Claude config dir (default ~/.claude)")
    ap.add_argument("--top", type=int, default=5, help="agents/skills listed per domain")
    args = ap.parse_args()
    home = Path(args.home)
    agents, skills = load(home)
    index = build(agents, skills, args.top)
    prov = providers()
    (home / "agent-index.md").write_text(render(index, len(agents), len(skills), prov), encoding="utf-8")
    (home / "agent-index.json").write_text(
        json.dumps({"domains": index, "providers": prov}, indent=2), encoding="utf-8"
    )
    print(f"indexed {len(agents)} agents, {len(skills)} skills -> {home}/agent-index.md")


if __name__ == "__main__":
    main()
