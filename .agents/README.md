# .agents/

Home for multi-step procedures ("skills") that AI agents can invoke when working
in this repo.

## Skills

| Skill | What it does |
| --- | --- |
| [`write-e2e`](write-e2e/SKILL.md) | Scaffold a SeleniumBase E2E test under `tests/e2e/new_selenium/` using the `HopeTestBrowser` fixture API. **Canonical example** — copy its structure when adding a new skill. |
| [`write-uts`](write-uts/SKILL.md) | Scaffold a pytest unit test under `tests/unit/` using the shared factories and fixtures from `tests/extras/test_utils/`. |

Keep this table in sync when adding or removing a skill.

## Discovery

Skills live under `.agents/<skill-name>/`. Claude Code discovers them via a
committed symlink `.claude/skills → ../.agents`, so `/skill-name` works out of
the box after clone. Other agents (Codex, Cursor, plain markdown readers) read
the files directly from `.agents/` — they don't need the symlink.

## Layout

```
.agents/
├── README.md                 # this file
└── <skill-name>/
    ├── SKILL.md              # required — the procedure (the "agent")
    └── context.md            # optional — reference material the skill needs
```

One directory per skill, kebab-case name. `SKILL.md` is required; supporting
files (`context.md`, templates, example payloads) sit next to it in the same
directory.

## SKILL.md frontmatter

```yaml
---
name: skill-name
description: One-line summary of what the skill does. USE WHEN <concrete user intents or contexts that should trigger this skill>.
---
```

`description` is what agents see when deciding whether to invoke the skill —
make it specific. The `USE WHEN` clause describes the trigger conditions
inline; a separate `trigger:` field is redundant, don't add one.

## SKILL.md body

Sections, in order:

1. **Title + one-line purpose** — what the skill produces.
2. **Inputs from user** — what the user must provide; ask before doing anything
   else if any input is missing.
3. **MANDATORY: read these before writing anything** — numbered list of files
   the agent must read first, including at least one concrete example file (not
   a `<placeholder>` path).
4. **Procedure** — numbered steps. Keep procedural (where files go, what to
   scaffold, what to run). Do not duplicate rules or reference material that
   lives elsewhere — point at it.
5. **Verify before reporting done** — exact commands to run.
6. **Refuse / push back if asked for** — bullet list of requests the skill must
   reject, so the agent pushes back instead of silently producing bad output.
