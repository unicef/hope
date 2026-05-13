# agents/

Home for multi-step procedures ("skills") that AI agents can invoke when working
in this repo.

## What is a skill?

A skill is a repeatable, multi-step procedure documented in one place. Examples:
"review a HOPE task PR", "scaffold a new task directory", "run a regression
check before release". If a behavior fits in a single rule ("always use X"), it
belongs in `AGENTS.md` or `docs/`. If it has steps, inputs, outputs, and decision
points, it is a skill.

## Layout

```
agents/
├── README.md                 # this file
└── <skill-name>/
    └── SKILL.md              # the procedure
```

One directory per skill, kebab-case name, a single `SKILL.md` inside. Extra
assets (templates, fixtures, example payloads) sit next to `SKILL.md` in the
same directory.

## SKILL.md frontmatter

```yaml
---
name: skill-name
description: One-line summary used to decide when to invoke this skill.
trigger: When the user asks X / when working on Y.
---
```

The body is plain Markdown and should cover: prerequisites, inputs, steps,
expected outputs, and known failure modes.

## Rules vs. skills

|         | Rules                              | Skills                              |
| ------- | ---------------------------------- | ----------------------------------- |
| Where   | `AGENTS.md`, `docs/`               | `agents/<name>/SKILL.md`            |
| Shape   | Always-true constraints            | Step-by-step procedures             |
| Example | "Maintain 97% coverage on new code" | "Open a code review on this PR"    |

A rule says *what must be true*. A skill says *how to do something*.

## Phase 1

No `SKILL.md` files are committed yet — this directory documents the convention
so future skills land in a consistent place.
