#!/usr/bin/env bash
# Rebuilds, on YOUR computer, the agents and skills installed during the cloud session.
# Safe to re-run: by default never overwrites existing agents/skills; pulls the latest upstream sources.
# Usage: bash setup-claude-local.sh [--update] [--skip-agency] [--skip-skills]
#   --update  also refresh already-installed agents/skills whose upstream content changed
#             (needed once to swap older same-named agents for the VoltAgent versions)
set -euo pipefail

CLAUDE="${HOME}/.claude"
VENDOR="${CLAUDE}/vendor"
AGENTS="${CLAUDE}/agents"
SKILLS="${CLAUDE}/skills"
mkdir -p "$VENDOR" "$AGENTS" "$SKILLS"

SKIP_AGENCY=0; SKIP_SKILLS=0; UPDATE=0
for a in "$@"; do
  case "$a" in --skip-agency) SKIP_AGENCY=1;; --skip-skills) SKIP_SKILLS=1;; --update) UPDATE=1;; esac
done

sync_repo() {  # sync_repo <url> <dir>
  if [ -d "$2/.git" ]; then git -C "$2" pull -q --ff-only || true
  else GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 "$1" "$2"; fi
}

copy_new() {   # copy_new <src> <dest> -- copy if missing; with --update, replace if content differs
  local name dest; name="$(basename "$1")"; dest="$2/$name"
  if [ ! -e "$dest" ]; then
    cp -r "$1" "$2/" && echo "  + $name"
  elif [ "$UPDATE" -eq 1 ] && ! diff -rq "$1" "$dest" >/dev/null 2>&1; then
    rm -rf "$dest" && cp -r "$1" "$2/" && echo "  ~ $name (updated)"
  fi
}

CLAIMED="$(mktemp)"; trap 'rm -f "$CLAIMED"' EXIT
copy_agents() {  # copy_agents <glob...> -- earlier calls win on same-named agents
  local f b
  for f in "$@"; do
    b="$(basename "$f")"
    [ "$b" = README.md ] && continue
    grep -qxF "$b" "$CLAIMED" && continue
    echo "$b" >> "$CLAIMED"
    copy_new "$f" "$AGENTS"
  done
}

echo "== Agents: VoltAgent/awesome-claude-code-subagents (~161, tool-restricted; wins on name clashes) =="
sync_repo https://github.com/VoltAgent/awesome-claude-code-subagents "$VENDOR/voltagent-subagents"
copy_agents "$VENDOR"/voltagent-subagents/categories/*/*.md

echo "== Agents: weaponslab/claude-agents (83; only names VoltAgent doesn't have) =="
sync_repo https://github.com/weaponslab/claude-agents "$VENDOR/weaponslab-claude-agents"
copy_agents "$VENDOR"/weaponslab-claude-agents/*.md

if [ "$SKIP_AGENCY" -eq 0 ]; then
  echo "== Agents: msitarzewski/agency-agents (engineering, security, marketing) =="
  sync_repo https://github.com/msitarzewski/agency-agents "$VENDOR/agency-agents"
  (cd "$VENDOR/agency-agents" && ./scripts/install.sh --tool claude-code \
      --division engineering,security,marketing --no-interactive) || echo "  (agency-agents install failed; continuing)"
fi

if [ "$SKIP_SKILLS" -eq 0 ]; then
  echo "== Skills: OneWave-AI/claude-skills (229; includes design-export-repair) =="
  sync_repo https://github.com/OneWave-AI/claude-skills.git "$VENDOR/onewave-claude-skills"
  for d in "$VENDOR"/onewave-claude-skills/*/; do
    [ -f "$d/SKILL.md" ] && copy_new "${d%/}" "$SKILLS"
  done

  echo "== Skills: coreyhaines31/marketingskills (50) =="
  sync_repo https://github.com/coreyhaines31/marketingskills "$VENDOR/marketingskills"
  for d in "$VENDOR"/marketingskills/skills/*/; do
    [ -f "$d/SKILL.md" ] && copy_new "${d%/}" "$SKILLS"
  done

  echo "== Skills: ruvnet/ruflo (SKILL.md only, not the 143 MB bundle) =="
  sync_repo https://github.com/ruvnet/ruflo "$VENDOR/ruflo"
  mkdir -p "$SKILLS/ruflo"; [ -e "$SKILLS/ruflo/SKILL.md" ] || cp "$VENDOR/ruflo/SKILL.md" "$SKILLS/ruflo/SKILL.md"

  echo "== Skills: guarded-provider-routing (from constapo/Inonda) =="
  sync_repo https://github.com/constapo/Inonda "$VENDOR/inonda"
  git -C "$VENDOR/inonda" fetch -q origin claude/install-claude-code-tool-vxzynm --depth 1 || true
  git -C "$VENDOR/inonda" checkout -q FETCH_HEAD -- .claude/skills/guarded-provider-routing 2>/dev/null \
    && copy_new "$VENDOR/inonda/.claude/skills/guarded-provider-routing" "$SKILLS" \
    || echo "  (could not fetch guarded-provider-routing; branch may be merged/renamed)"
fi

cat <<'EOF'

Done. Restart Claude Code to load the new agents and skills.
Optional extras used with design-export-repair:  pip install python-pptx PyMuPDF   (+ LibreOffice)
Tip: ~280 skills is a lot. If some trigger too eagerly, delete their folders from ~/.claude/skills/.
EOF
