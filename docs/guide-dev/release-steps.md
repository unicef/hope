---
title: Release steps
---

# Release steps

Manual steps a deploy needs — a new secret, a management command, a check afterwards — are
listed in [`RELEASE_STEPS.md`](https://github.com/unicef/hope/blob/develop/RELEASE_STEPS.md).

## Adding a step

In your PR, add one line as the first entry under `## Unreleased`:

```markdown
- **post-deploy** @owner #PR: Run `manage.py backfill_actor_snapshot` on all environments (~20 min, safe to rerun).
```

- `pre-deploy` or `post-deploy` — before or after the new code goes out.
- `@owner` — who makes sure it gets done.
- `#PR` — PR number.
- description — what to do, on which environments, how long, safe to rerun.

## Releasing to staging

Before opening the `develop` → `staging` PR, open a PR to `develop` that adds
`## <version>` (from `pyproject.toml`) right below `## Unreleased`, so its entries now belong
to the version. If the heading already exists (second staging release of the same version),
move it up to the same place. If `## Unreleased` is empty, skip this.

A CI check blocks PRs to `staging` and `master` while `## Unreleased` has entries.

## Hotfixes

Add the step under the heading of the version you are fixing, not under `## Unreleased`.

## Deploying to production

Copy the lines the `staging` → `master` PR adds to `RELEASE_STEPS.md` into its description
as a checklist:

```markdown
## Release steps
- [ ] **pre-deploy** @asmith #6590: Add the `KOBO_API_TOKEN` secret.
```

## Merging

Merge into `staging` and `master` with a merge commit, not a squash — otherwise the next PR
shows already released steps again.
