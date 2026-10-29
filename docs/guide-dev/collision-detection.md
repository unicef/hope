---
title: Collision Detection
tags:
  - program
  - rdi
  - household
  - strategy-field
---

# Collision Detection

Collision detection merges an incoming household into an existing household when both carry
the same identification key. This page describes the detector contract, the merge algorithm,
the entry points that invoke it, and the data model it relies on.

User-facing behaviour: [Collision Detection](../guide-user/collision-detection.md).
Programme configuration: [Collision Detection Configuration](../guide-adm/collision-detection.md).

## Where the code lives

| Component | Location |
|---|---|
| Detector base class, implementations, registry | `src/hope/apps/program/collision_detectors.py` |
| Programme field and registry wiring | `src/hope/models/program.py` (`collision_detector`) |
| Django Admin exposure | `src/hope/admin/program.py` (`ProgramAdminForm`) |
| RDI merge entry point | `src/hope/apps/registration_data/tasks/rdi_merge.py` (`RdiMergeTask._process_collisions`) |
| Ingestion API entry point | `src/hope/api/endpoints/rdi/mixin.py` (`HouseholdUploadMixin._manage_collision`) |
| LAX household push | `src/hope/api/endpoints/rdi/lax.py` (`CreateLaxHouseholds`) |
| Deduplication exclusion | `src/hope/apps/registration_data/tasks/deduplicate.py` (`collided_individuals_ids_to_exclude`) |

## Configuration and wiring

`Program.collision_detector` is a `strategy_field.fields.StrategyField` backed by
`collision_detectors_registry`:

```python
collision_detector = StrategyField(
    registry=collision_detectors_registry,
    default="hope.apps.program.collision_detectors.NoopCollisionDetector",
    help_text="Object which detects collisions",
)
```

- The field stores the fully qualified class name of the selected detector.
- Accessing `program.collision_detector` returns an **instance** of that class, constructed
  with the programme as its only argument (`StrategyField` uses
  `factory=lambda klass, obj: klass(obj)`).
- The registry contains `IdentificationKeyCollisionDetector` and `NoopCollisionDetector`:

```python
collision_detectors_registry: Registry = Registry(AbstractCollisionDetector)
collision_detectors_registry.append(IdentificationKeyCollisionDetector)
collision_detectors_registry.append(NoopCollisionDetector)
```

The default is the no-op detector. Migration
`src/hope/apps/program/migrations/0012_migration.py` replaced the former
`collision_detection_enabled` boolean and populated `NoopCollisionDetector` on existing
programmes.

## Detector contract

A detector receives the programme in `__init__` and implements two methods:

```python
class AbstractCollisionDetector:
    def __init__(self, context: Program):
        self.program = context

    def detect_collision(self, household: Household) -> str | None: ...

    def update_household(self, household_to_merge: Household) -> None: ...
```

- `detect_collision` returns the string id of the existing household that collides with the
  incoming household, or `None`.
- `update_household` performs the merge. `NoopCollisionDetector` implements both methods as
  no-ops.
- `AbstractCollisionDetector` also provides the helpers used by the identification key
  detector: `_update_roles_in_household`, `_update_individual_identities`,
  `_update_documents`, `_update_accounts`, `_update_individual`, `_update_household`,
  `_update_db_instance`, and `_process_removed_individual`.

## Detection

`IdentificationKeyCollisionDetector` builds an in-memory index on first use:

1. `initialize` queries `Household` rows of the programme that have a non-null
   `identification_key` and maps `identification_key` to the household id.
2. The index is cached on the detector instance, so repeated calls do not re-query.
3. `detect_collision` returns `None` when the incoming household has no key. Otherwise it
   looks the key up in the index and returns the matching household id, if any.

The detector only compares households in the same programme. The physical uniqueness
guarantee comes from database constraints on `(identification_key, program)` for merged,
non-removed households on both `Household` and `Individual`
(`identification_key_unique_constraint`, `identification_key_ind_unique_constraint`).

## Merge algorithm

`IdentificationKeyCollisionDetector.update_household` is wrapped in `transaction.atomic` and
runs these steps:

1. Return immediately when the incoming household has no identification key.
2. Resolve the destination household through `detect_collision`; return when there is no
   match.
3. Validate that every individual in both households has an identification key. A missing key
   raises `ValueError` with a message naming the household, which aborts the surrounding
   merge transaction.
4. Partition members by identification key into three sets: keys to update (present on both
   sides), keys to add (only in the incoming household), and keys to remove (only in the
   existing household).
5. Store the incoming roles by individual identification key, because the role rows are
   deleted when members are processed.
6. Store the incoming head of household's identification key and clear
   `head_of_household` on the destination household. The protected foreign key must be
   cleared before the source household is deleted.
7. For keys to update, apply the incoming member's data to the existing member:
   - `_update_documents` replaces destination documents with source documents and keeps the
     destination status when the `(document_number, type_id)` pair matches.
   - `_update_individual_identities` deletes destination identities and reassigns source
     identities.
   - `_update_accounts` deletes destination accounts and reassigns source accounts.
   - `_update_individual` copies scalar fields with `model_to_dict`, excluding identifiers,
     collections, programme, registration import, merge status, and household.
8. For keys to remove, `_process_removed_individual` stores
   `internal_data["removed_by_collision_detector"]` with the previous relationship, previous
   roles, and whether the member was head of household; sets the relationship to
   `REMOVED_BY_COLLISION`; deletes the member's role rows; and calls
   `withdraw(notify=False)` unless the member is already withdrawn.
9. For keys to add, reassign the member's `household` to the destination and set
   `rdi_merge_status` to `MERGED`.
10. Re-read the destination members, rebuild roles with `_update_roles_in_household`, and set
    the new head of household.
11. Copy the incoming household's scalar fields onto the destination with
    `_update_household`. That helper excludes identifiers, collections, programme,
    registration import, merge status, `extra_rdis`, representatives, and the head of
    household. It then clears the source head, deletes the source household with
    `delete(soft=False)`, and sets `head_of_household` on the destination.

`_update_db_instance` uses `model_to_dict`, removes many-to-many fields, and applies the
result with a queryset `update()`.

## Entry points

### RDI merge

`RdiMergeTask._process_collisions` runs inside the merge transaction:

1. Read `obj_hct.program.collision_detector`.
2. Iterate pending households in chunks of 1000, requesting only `id` and
   `identification_key`.
3. Collect the pending household ids to exclude and the destination household ids.
4. Lock every destination household in primary-key order with one
   `select_for_update().order_by("pk")` statement, to avoid deadlocks.
5. Call `update_household` for each colliding pending household.
6. Add the destination ids to `obj_hct.extra_hh_rdis`.
7. Return the ids to merge, the ids to exclude, and the destination ids.

The caller then:

- excludes individuals whose household is in the excluded set from the merge;
- schedules `recalculate_population_fields_async_task` for the merged households **and**
  the collided destination households, because withdrawing members changes their counters;
- marks the import as merged and emits `rdi_merged`, which triggers `adjust_program_size`.

### Ingestion API upload

`HouseholdUploadMixin._manage_collision` resolves collisions at upload time:

1. Call `detect_collision` on the incoming household.
2. When there is no match, return `None` and let the normal upload path create the pending
   household.
3. When there is a match, build `model_to_dict` with `_COLLISION_EXCLUDE_FIELDS`, drop keys
   whose value is `None` (so existing data is not overwritten with NULL), and update the
   destination household with a queryset `update()`.
4. Return the destination id. The caller adds it to `extra_hh_rdis` and skips creating the
   pending household.

This scalar-only path is used by:

- `RDINestedSerializer` in `src/hope/api/endpoints/rdi/upload.py`;
- `CountryWorkspaceHouseholdSerializer` in `src/hope/api/endpoints/rdi/upload.py`;
- the Country Workspace household push view in `src/hope/api/endpoints/rdi/base.py`;
- `CreateLaxHouseholds` in `src/hope/api/endpoints/rdi/lax.py`.

It does not run the member-level merge. In the LAX flow, individuals are pushed before the
household; when the household collides and is skipped, the individuals follow the normal
merge path on their own.

### Deduplication

`DeduplicateTask.collided_individuals_ids_to_exclude` loads the households of the importing
RDI, keeps the ids of households whose key collides with an existing household, and returns
the pending individual ids that belong to those households. `deduplicate_pending_individuals`
passes that list as the exclusion set, so members of colliding households are not scored
against the population again.

## Concurrency and signals

- Destination households are locked in primary-key order before any writes. This matches the
  lock ordering used by population recalculation and avoids deadlocks between concurrent
  merges.
- `withdraw(notify=False)` avoids emitting `individual_withdrawn` once per removed member.
  The programme size adjustment signal is driven by `rdi_merged` at the end of the merge, so
  one merge produces one recalculation signal instead of one per withdrawn member.
- `_process_collisions` requests only `id` and `identification_key` from pending households.
  The query-count test asserts that detection stays at a constant query count regardless of
  household count; adding a deferred field read would break it.

## Data model

| Field or constraint | Location | Purpose |
|---|---|---|
| `Household.identification_key` | `src/hope/models/household.py` | Household-level match key, up to 255 characters, nullable. |
| `Individual.identification_key` | `src/hope/models/individual.py` | Member-level match key used during the merge, up to 255 characters, nullable. |
| `Household.extra_rdis` | `src/hope/models/household.py` | Many-to-many link to the registration data imports that collided with the household. |
| `identification_key_unique_constraint` | `src/hope/models/household.py` | Unique `(identification_key, program)` for merged, non-removed households. |
| `identification_key_ind_unique_constraint` | `src/hope/models/individual.py` | Same uniqueness rule for individuals. |
| `REMOVED_BY_COLLISION` | `src/hope/apps/household/const.py` | Relationship value assigned to members withdrawn by a collision. |
| `internal_data["removed_by_collision_detector"]` | Individual `internal_data` JSON field | Audit snapshot of the previous relationship, roles, and head-of-household status. |

`Individual.withdraw` invalidates the member's documents, deactivates accounts, sets
`withdrawn` and `withdrawn_date`, and saves the record. With `notify=False` it does not emit
the withdrawal signal.

## Extending collision detection

To add a detector:

1. Subclass `AbstractCollisionDetector` and store the programme from `__init__`.
2. Implement `detect_collision(household) -> str | None` and
   `update_household(household_to_merge) -> None`.
3. Register the class in `collision_detectors_registry` so it appears in the Django Admin
   choice list.
4. Add tests for detection, merge, and the no-match path. Use
   `tests/unit/apps/program/test_collision_detector.py` as the reference.

## Tests

| File | Coverage |
|---|---|
| `tests/unit/apps/program/test_collision_detectors.py` | Null identification key returns no collision. |
| `tests/unit/apps/program/test_collision_detector.py` | Merge helpers, household update, removed-member withdrawal, already-withdrawn members. |
| `tests/unit/apps/registration_data/test_rdi_merge_collision.py` | RDI merge collisions, multiple targets, query count, recalculation scheduling, signal suppression. |
| `tests/unit/apps/registration_data/test_deduplicate_collisions.py` | Collided individuals excluded from deduplication. |
| `tests/unit/api/test_lax_collision_integration.py` | End-to-end LAX upload and merge with a collision. |

Run the relevant files with the `tests` tox environment. The `tests` environment replaces its
whole default command when arguments follow `--`, so `pytest` and its flags must be repeated:

```bash
tox -e tests -- pytest -q --no-migrations --randomly-seed=42 --create-db -n auto --dist=loadgroup tests/unit/apps/program/test_collision_detector.py tests/unit/apps/program/test_collision_detectors.py tests/unit/apps/registration_data/test_rdi_merge_collision.py tests/unit/apps/registration_data/test_deduplicate_collisions.py tests/unit/api/test_lax_collision_integration.py
```

The LAX integration and RDI merge tests use Elasticsearch fixtures; start the local services
described in [Testing](testing.md) before running them.
