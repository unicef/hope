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
the same identification key. This page describes the detector contract, how detection works,
where the collision step runs, and the data model it relies on. The code is the reference for
the step-by-step behaviour.

User-facing behaviour: [Collision Detection](../guide-user/collision-detection.md).
Programme configuration: [Collision Detection Configuration](../guide-adm/collision-detection.md).

## Where the code lives

| Component | Location |
|---|---|
| Detector base class, implementations, registry | [`src/hope/apps/program/collision_detectors.py`](https://github.com/unicef/hope/blob/develop/src/hope/apps/program/collision_detectors.py) |
| Programme field and registry wiring | [`src/hope/models/program.py`](https://github.com/unicef/hope/blob/develop/src/hope/models/program.py) (`collision_detector`) |
| Django Admin exposure | [`src/hope/admin/program.py`](https://github.com/unicef/hope/blob/develop/src/hope/admin/program.py) (`ProgramAdminForm`) |
| Collision step of the RDI merge | [`src/hope/apps/registration_data/tasks/rdi_merge.py`](https://github.com/unicef/hope/blob/develop/src/hope/apps/registration_data/tasks/rdi_merge.py) (`RdiMergeTask._process_collisions`, called from `RdiMergeTask.execute`) |
| Country Workspace auto-merge | [`src/hope/api/endpoints/rdi/base.py`](https://github.com/unicef/hope/blob/develop/src/hope/api/endpoints/rdi/base.py) (`CompleteRDIView`), [`src/hope/apps/registration_data/tasks/rdi_merge_dispatcher.py`](https://github.com/unicef/hope/blob/develop/src/hope/apps/registration_data/tasks/rdi_merge_dispatcher.py) (`RdiMergeDispatcher`) |
| Deduplication exclusion | [`src/hope/apps/registration_data/tasks/deduplicate.py`](https://github.com/unicef/hope/blob/develop/src/hope/apps/registration_data/tasks/deduplicate.py) (`collided_individuals_ids_to_exclude`) |

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

The default is the no-op detector.

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
  `_update_documents`, `_update_accounts`, `_update_individual`, `_update_biometric_pairs`,
  `_update_household`, `_get_update_data`, `_record_replaced_ids`,
  `_restore_removed_by_collision`, and `_process_removed_individual`.

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

## Collision-Merge algorithm

`IdentificationKeyCollisionDetector.update_household` takes a pending household that collides
with a household already in the population. It keeps the existing household and its HOPE
identifiers, updates members matched by individual identification key, moves new members in,
withdraws members that are no longer present, rebuilds roles, copies the incoming data, and
hard-deletes the incoming household. A member without an identification key raises
`ValueError` and aborts the merge.

## Entry points

### RDI merge

`RdiMergeTask.execute` calls `_process_collisions` inside the merge transaction. It locks the
destination households in primary-key order, calls `update_household` for each colliding
pending household, and links the import to the destinations through `extra_hh_rdis`. The
merge then skips the collided pending households and recalculates the population counters of
the destinations as well.

### Ingestion API uploads

The API endpoints do not resolve collisions. Every path stores the incoming household and
its members as pending rows with their identification keys and leaves the match to
`RdiMergeTask._process_collisions`, so an API import goes through the same merge as an XLSX
or Kobo import.

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
- Source members are not deleted one by one. `_update_individual` only clears their unique
  ids; the hard delete of the source household in `_update_household` cascades them, so the
  merge runs the Django collector once per household and sends no `individual_deleted` per
  member. The source household is deleted before its data is copied, because
  `originating_id` is unique among live households.
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
| `Individual.country_workspace_id`, `Individual.originating_id` | `src/hope/models/individual.py` | External ids taken over from the incoming member. Unique among live rows (`country_workspace_id_ind_unique_constraint`, `originating_id_ind_unique_constraint`), which is why the source ids are cleared before the copy. |
| `Household.originating_id` | `src/hope/models/household.py` | External id taken over from the incoming household. Unique among live rows (`originating_id_hh_unique_constraint`), which is why the source household is deleted before the copy. |
| `REMOVED_BY_COLLISION` | `src/hope/apps/household/const.py` | Relationship value assigned to members withdrawn by a collision. |
| `internal_data["removed_by_collision_detector"]` | Individual `internal_data` JSON field | Audit snapshot of the previous relationship, roles, head-of-household status, and `withdrawn_by_collision`. Removed again when a later collision brings the member back. |
| `internal_data["collision_replaced_ids"]` | Individual and Household `internal_data` JSON field | List with one entry per collision holding the `country_workspace_id` and `originating_id` the record had before the incoming values replaced them. |

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
| `tests/unit/apps/program/test_collision_detector.py` | Merge helpers, household update, removed-member withdrawal, already-withdrawn members, kept system fields, replaced ids, restored members, biometric pairs. |
| `tests/unit/apps/registration_data/test_rdi_merge_collision.py` | RDI merge collisions, multiple targets, query count, recalculation scheduling, withdrawn and deleted signal suppression. |
| `tests/unit/apps/registration_data/test_deduplicate_collisions.py` | Collided individuals excluded from deduplication. |
| `tests/unit/api/test_lax_collision_integration.py` | End-to-end LAX upload and merge with a collision. |
| `tests/unit/api/test_upload.py` | Nested upload saves a colliding household as pending; blank identification key rejected, null accepted. |
| `tests/unit/api/test_lax_households.py`, `tests/unit/api/test_lax_individuals.py`, `tests/unit/api/test_push_people.py` | LAX household push saves a colliding household as pending; blank identification key rejected. |

For how to run them, see [Testing](testing.md).
