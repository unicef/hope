---
title: Collision Detection
tags:
  - Registration
  - Population Management
  - Programme Management
---

# Collision Detection

Collision detection keeps one household record per real household when registration data
contains a household that already exists in the programme population. HOPE matches the
incoming household against existing households by **identification key**. When the keys
match, HOPE updates the existing household instead of creating a duplicate.

This page is for programme managers and registration staff. A HOPE administrator enables
the detector separately for each programme; see
[Collision Detection Configuration](../guide-adm/collision-detection.md).

## How HOPE matches households

- Matching is scoped to a single programme. A household in another programme never collides
  with the incoming record.
- The match uses the household **identification key**. HOPE compares the key on the incoming
  household with the keys of households already in the programme population.
- A household without an identification key never collides. The same applies to a blank key.
- Individual members also carry an identification key. HOPE uses it to decide which members
  the incoming household keeps, adds, or removes during a merge.
- Within a programme, an identification key must be unique among merged, non-removed
  households. HOPE enforces this with a database constraint.

The identification key can arrive through the registration import. The ingestion API accepts
it as the `identification_key` field. XLSX imports use the `identification_key_h_c` and
`identification_key_i_c` columns, and people rows accept a `pp_identification_key` column.
The key can also be edited through grievance data changes when the change is approved.

The label shown for the individual identification key is configurable per programme. See
[Identification Key](population.md#identification-key).

## When HOPE resolves a collision

Collision detection runs during registration data processing. The exact moment depends on
how the data enters HOPE:

| Entry path | When the collision is resolved | Effect |
|---|---|---|
| Registration data import (RDI) merge | While pending households are merged into the population | Full household and member merge, described below |
| Ingestion API upload, including Country Workspace and LAX pushes | While the household is uploaded | The existing household's own fields are updated; no second household is created |

When the collision is resolved at upload time, the member-level merge described below does
not run. The existing household keeps its members until another import or merge changes
them.

## What happens during a full merge

When a collision is resolved during the RDI merge, HOPE treats the existing household as the
destination and the incoming household as the source:

1. The existing household keeps its HOPE identifiers, including its `unicef_id`.
2. Members present in both households are matched by their individual identification key.
   The incoming data updates the existing member. Documents, identities, and accounts from
   the incoming member replace those on the existing member.
3. Members that exist only in the incoming household are moved into the existing household.
4. Members that exist only in the existing household are **withdrawn, not deleted**. Their
   relationship is set to **Removed by collision**, their household roles are removed, their
   documents are invalidated, and their accounts are deactivated.
5. The head of household and the primary and alternate collector roles are rebuilt from the
   incoming household.
6. The incoming household's data replaces the existing household's data, except for system
   fields such as identifiers, programme, registration import, and merge status.
7. The incoming household record is deleted. The existing household remains.
8. The registration data import that contained the incoming household is linked to the
   existing household as an **extra RDI**.
9. HOPE recalculates the household's population counters after the merge.

If any member of either household has no identification key, HOPE cannot complete the merge
and stops with an error. See [Troubleshooting](#troubleshooting).

## What happens to removed members

A member removed by a collision is not deleted:

- The individual remains in the programme population with the same identifiers.
- The individual is marked as withdrawn.
- The relationship is set to **Removed by collision**.
- The previous relationship, the previous household roles, and whether the individual was
  head of household are kept in the individual's internal data under
  `removed_by_collision_detector`.

This preserves the audit trail of what the member was before the merge.

## What collision detection does not do

- It is not deduplication. Collision detection uses an exact identification key match, while
  deduplication scores individuals for similarity. Members of colliding households are
  excluded from deduplication because the collision already identifies the household.
- It does not merge records across programmes.
- It does not merge existing records retroactively. Enabling the detector affects subsequent
  imports and merges only.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Two households with the same key remain in the population | The detector is set to the no-op detector for the programme | Ask an administrator to enable the identification key detector; see [Collision Detection Configuration](../guide-adm/collision-detection.md) |
| No collision is detected for an incoming household | The incoming household has no identification key, or its key differs from the existing household | Check the key in the import file or API payload |
| No collision is detected | The household belongs to a different programme | Confirm the programme on both records |
| The merge stops with `Cannot merge households with individuals with no identification key` | At least one member in either household has no individual identification key | Populate the missing individual keys, then run the merge again |
| Members are missing after an upload resolved the collision | The upload-shortcut path updates only the household's own fields | Run a subsequent registration data import and merge, or correct the members directly |

## Next steps

- [Collision Detection Configuration](../guide-adm/collision-detection.md) -- enable the
  detector for a programme and review its settings.
- [Identification Key](population.md#identification-key) -- where the key appears on the
  individual record.
- [Collision Detection](../guide-dev/collision-detection.md) -- implementation details for
  developers.
