#!/usr/bin/env bash
# Rebuilds, on YOUR computer, the agents and skills installed during the cloud session.
# Safe to re-run: never overwrites an existing agent/skill; updates the cloned sources.
# Usage: bash setup-claude-local.sh [--skip-agency] [--skip-skills]
set -euo pipefail

CLAUDE="${HOME}/.claude"
VENDOR="${CLAUDE}/vendor"
AGENTS="${CLAUDE}/agents"
SKILLS="${CLAUDE}/skills"
mkdir -p "$VENDOR" "$AGENTS" "$SKILLS"

SKIP_AGENCY=0; SKIP_SKILLS=0
for a in "$@"; do
  case "$a" in --skip-agency) SKIP_AGENCY=1;; --skip-skills) SKIP_SKILLS=1;; esac
done

sync_repo() {  # sync_repo <url> <dir>
  if [ -d "$2/.git" ]; then git -C "$2" pull -q --ff-only || true
  else GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 "$1" "$2"; fi
}

copy_new() {   # copy_new <src> <dest> -- copy file/dir only if it doesn't exist yet
  local name; name="$(basename "$1")"
  [ -e "$2/$name" ] && return 0
  cp -r "$1" "$2/" && echo "  + $name"
}

echo "== Agents: weaponslab/claude-agents (83) =="
sync_repo https://github.com/weaponslab/claude-agents "$VENDOR/weaponslab-claude-agents"
for f in "$VENDOR"/weaponslab-claude-agents/*.md; do
  [ "$(basename "$f")" = README.md ] && continue
  copy_new "$f" "$AGENTS"
done

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
