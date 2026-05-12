# AGENTS.md

UNICEF HOPE (Humanitarian cash Operations and Programme Ecosystem) — Django + React
platform for humanitarian cash transfers. Backend lives in `src/`, frontend in
`src/frontend/`, tests in `tests/`.

## Run tests

Local Makefile shortcuts (auto-start required Docker services):

```bash
make uts                          # all unit tests
make uts ARGS="-k test_create"    # filter by name
make uts ONLY="household"         # narrow to one app
make e2e                          # Selenium end-to-end tests
```

For canonical pytest/tox invocations, Docker-based runs, and coverage rules, see:

@docs/guide-dev/testing.md

## Skills

Multi-step procedures (review flows, scaffolding routines, etc.) live under
`agents/` — see `agents/README.md` for the convention.
