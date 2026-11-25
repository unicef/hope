---
title: Collision Detection Configuration
tags:
  - Configuration
  - Programme Management
  - Django Admin
---

# Collision Detection Configuration

Sources:
[`collision_detectors.py`](https://github.com/unicef/hope/blob/develop/src/hope/apps/program/collision_detectors.py),
[`models/program.py`](https://github.com/unicef/hope/blob/develop/src/hope/models/program.py),
[`admin/program.py`](https://github.com/unicef/hope/blob/develop/src/hope/admin/program.py),
[`IndividualBioData.tsx`](https://github.com/unicef/hope/blob/develop/src/frontend/src/components/population/IndividualBioData/IndividualBioData.tsx)

Collision detection is configured per programme. This page is for HOPE administrators who
have access to the Django Admin and need to enable, review, or disable the feature.

For the user-facing behaviour, see [Collision Detection](../guide-user/collision-detection.md).
For the implementation, see [Collision Detection](../guide-dev/collision-detection.md).

## Configure the detector

1. Open the Django Admin.
2. Open the **Programme** section.
3. Select the programme you want to configure.
4. In the **Collision detector** field, choose one of the registered detectors:

   | Choice | Behaviour |
   |---|---|
   | `hope.apps.program.collision_detectors.NoopCollisionDetector` | Detection is off. This is the default. |
   | `hope.apps.program.collision_detectors.IdentificationKeyCollisionDetector` | Incoming households are matched against existing households by identification key. |

5. In the **Identification key individual label** field, optionally enter up to 255
   characters. HOPE shows this label for the individual identification key in the **Bio
   Data** section of the individual details page:
   `https://<HOPE host>/<business area>/programs/<programme id>/population/individuals/<individual id>`.
   Leave it blank to use the default label, **Identification Key**.
6. Save the programme.

There is no environment variable or Constance setting for collision detection. Both settings
are stored on the programme record.

## Before you enable detection

Check the following before switching a programme to the identification key detector:

- Households already in the programme population have an identification key where matching
  is expected. Households without a key are never matched.
- Every member of the households that will participate in a collision has an individual
  identification key. A merge stops with an error if a member is missing one.
- The identification key values are unique within the programme. HOPE enforces uniqueness
  among merged, non-removed households with a database constraint.
- The registration process supplies the key. Without a key in the incoming data, no
  collision can be detected.

Enabling the detector does not merge existing records. It applies to imports and merges that
start after the change.

## Operational effects

During a registration data import merge, a detected collision:

- updates the existing household instead of creating a new one;
- keeps the existing household's identifiers, including its `unicef_id`;
- keeps the fields HOPE manages itself on the existing household and its members:
  withdrawal, registration dates, cash received totals, duplicate and deduplication results,
  and sanction list flags;
- takes over the incoming country workspace id and originating id and keeps the previous
  values in the record's internal data under `collision_replaced_ids`, one entry per
  collision;
- withdraws members that are no longer present, sets their relationship to **Removed by
  collision**, and keeps the previous relationship and roles in their internal data;
- restores a member that an earlier collision removed when the incoming household contains
  that member again;
- links the incoming registration data import to the existing household as an extra RDI;
- recalculates the household's population counters.

Ingestion API uploads (nested, Country Workspace, LAX, and people pushes) store pending
records only. The collision is resolved when their import is merged; Country Workspace
imports are merged automatically once the push is completed.

## Verify and monitor

- In the **Household** section of the Django Admin, open the household and review the
  read-only **Extra RDIs** field. It lists the registration data imports that collided with
  the household.
- Review the individuals that are no longer in the household. They should be withdrawn with
  the relationship **Removed by collision**.
- The **Extra RDIs** household attribute is also available to targeting queries and XLSX
  exports, so reports can distinguish households that received colliding registrations.

## Disable or roll back

Set **Collision detector** back to `NoopCollisionDetector` to stop matching for subsequent
imports and merges. Disabling the detector does not undo a merge that already happened:
merged households stay merged, and withdrawn members stay withdrawn.

## Failure handling

If the merge reports:

```text
Cannot merge households with individuals with no identification key
```

at least one member of the existing household or of the incoming household has no
identification key. The merge transaction rolls back and the registration data import is not
merged. Populate the missing keys, then run the merge again.

What happens next depends on the source of the import:

- **XLSX, Kobo, or ingestion API nested upload**: a user started the merge, so the import
  ends in **Merge error** and nothing else is blocked.
- **Country Workspace push**: the merge runs automatically, so the import ends in **Merge
  error** and the programme's merge queue stops. Later Country Workspace imports of the
  programme wait until that import is retried or reset.

If a household has no identification key at all, it is accepted without collision
processing. Correct the key in the source data and import the household again if matching is
required.

## Related pages

- [Collision Detection](../guide-user/collision-detection.md) -- user-facing behaviour and
  troubleshooting.
- [Identification Key](../guide-user/population.md#identification-key) -- the field shown on
  the individual record.
- [Collision Detection](../guide-dev/collision-detection.md) -- detector contract and merge
  implementation.
