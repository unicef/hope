---
title: Migrations Baseline
tags:
  - migrations
  - database
---

# Migrations Baseline

The migrations production had applied when the baseline was written (361 files in 19 first-party
apps) were replaced by baseline migrations: one to three files per app that create that schema
directly. Each baseline file lists the old migrations it stands for in `replaces`, and the old files
are deleted. The 16 newer migrations, which only dev and staging had applied, stay as ordinary files
that depend on the baseline.

- A database that has the replaced migrations applied runs **nothing of the baseline**: `migrate`
  records the baseline names in `django_migrations` and then applies the ordinary migrations the
  database lacks. On production those are the 16 kept ones, on dev and staging none.
- An empty database runs the baseline and the migrations above it, and ends up with the same schema
  and seed rows the old chain produced.

## Rules

Each of these fails silently or destroys data when broken.

- **Do not delete rows from `django_migrations`** while baseline files carry `replaces`. Without the
  old rows Django sees the baseline as unapplied and executes it on the existing database.
- **Do not deploy the baseline to a database that lacks any replaced migration.** The old files are
  gone and cannot be applied any more. The baseline replaces only what `master` had, so dev, staging
  and production qualify; `migrate` refuses any other database (see [The guard](#the-guard)).
- **Do not remove `replaces`, the guard or the old rows in the same release as the baseline.** The
  cleanup is a separate, later release (see [Rollout](#rollout)).
- **Do not give a migration a name listed in `replaces`.** Every existing database has that name
  recorded as applied, so the migration would never run. `makemigrations` continues above the highest
  number on disk by itself (`payment/0084_migration.py` is the next one), and
  `tests/unit/apps/core/test_migration_baseline.py` fails when a name collides.
- **Do not add a baseline file without `replaces`.** It would execute on production.
- **Do not target `migrate` at a single app or migration on an empty database**, and do not reuse a
  database whose first `migrate` was interrupted. Rebuild it instead (see
  [Recovering a local database](#recovering-a-local-database)).

## What the baseline contains

| File | Content |
|---|---|
| `NNNN_baseline_models.py` | `CreateModel` with the fields as of the last replaced migration. Where the models need them, it starts with idempotent `RunSQL` for the `citext` extension, the `und-ci-det` collation and `check_unique_document_for_individual`. |
| `NNNN_baseline_relations.py`, `NNNN_baseline_relations_2.py` | Foreign keys, many-to-many fields, indexes and constraints that dependency cycles between apps keep out of the first file. The app's last file also holds the database objects and the seed rows below. |

An app that keeps later migrations has its baseline files under the number of the last migration they
replace: `payment/0081_baseline_models.py` and `payment/0081_baseline_relations.py` stand for `0001` to
`0081`, and the kept `payment/0082_migration.py` depends on the last of them. In the other apps the
baseline continues after the last old migration (`account/0036_baseline_models.py`).

Objects Django does not generate are created with top-level `RunSQL` at the end of the app's last
baseline file:

| Object | App |
|---|---|
| `unicef_id_index` serial column, its function and `BEFORE INSERT` trigger (11 tables) | `accountability`, `grievance`, `household`, `payment` |
| Triggers on `core_businessarea` that create the per business area sequences | `core`, `payment` |
| Triggers that fill `unicef_id` from those sequences | `payment`, `program` |
| `vector_column_trigger`, `generate_unique_program_registration_id` and its trigger, `household_household_default_page_index` | `household` |
| Partial indexes `idx_ra_user_no_expiry`, `idx_ra_partner_ba_no_exp`, `idx_ra_ba_no_expiry` | `account` |
| `funds_commitment_header_trigger_function`, `funds_commitment_insert_trigger` and the unused `funds_commitment_trigger_function` | `vision` |

Seed rows come from one `RunPython` per app, written with literals: currencies (`core`), the two
beneficiary groups production started with (`program`), account types and
the default payment plan purpose (`payment`), the UN sanction list (`sanction_list`). `program` also
writes the `DEFAULT_BENEFICIARY_GROUP_NAME` row of `constance_constance`, which the old chain stored
as a side effect of reading the setting.

### Legacy names

An empty database has to match the existing ones, including what the old history left behind:

- index, constraint and sequence names that `RenameModel` and `RenameField` did not update,
- the `(tree_id, lft)` indexes django-mptt declares, which no existing database has,
- an index on `payment_account.unique_key` that no model declares.

The baseline reproduces them with `ALTER ... RENAME`, `DROP INDEX IF EXISTS` and `CREATE INDEX IF NOT
EXISTS`. Removing such a quirk is an ordinary forward migration, not an edit of the baseline: the
baseline never runs on existing databases.

### Writing SQL in a baseline file

- Keep every `RunSQL` at the top level of `operations` and its `sql` a string or a list of strings.
  The test suites build their database from the models and then replay every top-level `RunSQL`
  from disk (`register_custom_sql_signal` in `tests/unit/conftest.py` and `tests/e2e/conftest.py`).
- A replayed statement may fail only with "already exists". Anything else has to be idempotent
  (`IF EXISTS`, `IF NOT EXISTS`, `CREATE OR REPLACE`).
- `CreateModel` and `AddField` create foreign keys and most indexes at the very end of the migration.
  A statement that touches them in the same migration goes into
  `hope.apps.core.migration_operations.RunSQLAfterDeferred`.
- `development_tools/db/premigrations.sql` creates the extension, the collation and the document
  function before the test tables exist. Keep it in line with the baseline.

## The guard

`manage.py migrate` is overridden in `hope.apps.core`. Before anything runs it reads
`django_migrations` and stops with an error in two cases (`hope.apps.core.baseline_guard`). This
covers `upgrade`, the `dev` entrypoint and direct calls.

| `django_migrations` of an app | `migrate` |
|---|---|
| Every replaced migration applied | Runs nothing, records the baseline names |
| No replaced migration applied (empty database) | Runs the baseline |
| Some replaced migrations applied | **Error**: `N of the M migrations replaced by the baseline are not applied in this database` |
| A row that is neither on disk nor in `replaces` | **Error**: `django_migrations has rows that are neither on disk nor replaced by the baseline` |

- **Not applied**: the database stopped somewhere in the replaced chain, below what production had
  when the baseline was written. Locally, see below.
- **Neither on disk nor replaced**: the database is ahead of the code. It ran a migration this code
  does not have: a newer release, a hotfix branch, or a feature branch you switched away from.
- Only first-party apps in `INSTALLED_APPS` are checked. Rows of removed apps are ignored.
- `core.0023_migration` is tolerated by exact name. It was on `develop` for five days (PR #5914 to
  PR #5941) before it was renumbered and never reached `staging` or `master`, so of the three
  environments only dev can hold the row.

`python manage.py migrate --plan` runs the guard and changes nothing, so it tells whether a database
is ready for the baseline.

## Recovering a local database

| Situation | What to do |
|---|---|
| Database on the last old migration | Nothing. `python manage.py migrate` records the baseline names. |
| Database behind (guard: *not applied*) | Check out the parent of the baseline merge commit, run `python manage.py migrate`, switch back, run it again. Or rebuild. |
| First `migrate` on a new database was interrupted or targeted | Rebuild. The database holds a part of the baseline that cannot be resumed. |
| A migration from another branch is applied (guard: *neither on disk nor replaced*) | Switch back to that branch and unapply it (`python manage.py migrate <app> <previous migration>`), or rebuild. |

Rebuild:

```bash
python manage.py dropalldb
python manage.py migrate
```

## Branches with their own migrations

A branch cut before the baseline has migrations that depend on deleted files.

1. Before merging `develop`, unapply your migrations on your local database
   (`python manage.py migrate <app> <last old migration>`), or plan to rebuild it.
2. Merge `develop` and delete your migration files.
3. Run `python manage.py makemigrations`. The new files are numbered above the baseline.

## Rollout

| Phase | What happens | Done when |
|---|---|---|
| Baseline | The baseline is merged to `develop` and released to staging and production the usual way. No migration freeze and no separate release come first. | Each environment has the baseline names in `django_migrations`. Dev and staging ran nothing, production ran only the kept migrations. |
| Cleanup | A separate, later release removes `replaces`, the guard and the `migrate` override, and runs `migrate <app> --prune` for the 19 apps. | No old first-party names are left in `django_migrations`. |

- Each environment deploys one branch (production `master`, staging `staging`, dev `develop`), so the
  migrations it has applied are the migration files of that branch. `master` is the furthest behind,
  and the baseline replaces exactly its 361 migrations, so every environment already has them.
  `migrate --plan` from the baseline code confirms it on the database itself: it lists the kept
  migrations the database lacks, or nothing.
- The baseline itself changes no schema, and the old code ignores the baseline names. Rolling back
  the release that brings it is therefore the same as rolling back any release with the kept
  migrations in it.
- The cleanup must wait until **all three** environments have recorded the baseline. Until then the old
  rows are the only thing that keeps the baseline from executing.
