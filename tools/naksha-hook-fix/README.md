# Naksha Stop-hook fix

## Problem
The naksha plugin's `hooks/hooks.json` has a `Stop` hook of `"type": "prompt"`. A prompt hook is
judged by a small model with no file access, yet the prompt asks it to read and write
`.naksha/project.json`, and never says what to answer when there is nothing to do. With no
`naksha-memory-update` blocks in the session it answers "insufficient evidence", which the harness
reports as hook feedback at the end of nearly every session.

## Fix
Replace the prompt hook with a command hook that does the same job deterministically
(`apply-memory-updates.py`): it scans the transcript for `<!-- naksha-memory-update {...} -->`
blocks, applies `project_json_patch` / `browser_finding_write` to `.naksha/project.json`
(searching up to 3 parent directories, array capped at 20, no duplicate re-adds), logs failures to
`~/.naksha/hook-errors.log`, prints nothing and always exits 0.

## Apply (on the machine where Claude Code runs)
1. Find the plugin: `find ~/.claude/plugins -path '*/hooks/hooks.json' | xargs grep -l naksha-memory-update`
2. Copy `apply-memory-updates.py` into that plugin's `scripts/` folder.
3. In that `hooks.json`, replace the whole `"Stop"` entry with:

```json
"Stop": [
  {
    "matcher": "*",
    "hooks": [
      {
        "type": "command",
        "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/apply-memory-updates.py\"",
        "timeout": 10
      }
    ]
  }
]
```
4. Restart Claude Code.

Plugin updates overwrite this, so also report it upstream, or disable the naksha plugin if you
don't use it (`/plugin`).
