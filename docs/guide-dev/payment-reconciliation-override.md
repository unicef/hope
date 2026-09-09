---
title: Payment Reconciliation Override
tags:
    - Payments
---

# Payment Reconciliation Override

## Scope

This feature changes manual XLSX reconciliation started from a Payment Plan Group.

The XLSX may contain some or all Payments from the group. Payments that are not present in the file remain unchanged.

It does not change:

- the household-based Follow-Up Instruction reconciliation importer;
- Payment Gateway reconciliation.

## Agreed behavior

### Status and delivered quantity

Manual Payment Plan Group XLSX processing uses the same pre-reconciliation state as Payment Gateway processing:

1. A newly created Payment starts in `PENDING`.
2. After the Payment is included in a successfully generated delivery XLSX, it moves to `SENT_TO_FSP`.
3. Reconciliation replaces `SENT_TO_FSP` with the distribution outcome.
4. An override reset returns the Payment to `SENT_TO_FSP`.

For this flow, `SENT_TO_FSP` means that HOPE generated an XLSX containing the Payment. It does not prove that a user
downloaded the file or that the FSP received it.

The current importer already derives `Payment.status` from delivered quantity:

- full amount → `DISTRIBUTION_SUCCESS`
- partial amount → `DISTRIBUTION_PARTIAL`
- zero → `NOT_DISTRIBUTED`
- any negative value → `ERROR`, storing quantity as `None`

Required changes:

- Accept only `-1` as the negative error marker. Store `delivered_quantity = None` and set
  `status = STATUS_ERROR`.
- Reject values such as `-2`; do not save any reconciliation changes for them.
- Return an `XlsxError` for invalid or non-numeric quantities.
- Update `Payment.status_date` whenever reconciliation changes `Payment.status`, and include `status_date` in the
  Payment `bulk_update` fields.

### Delivery export and historical Payments

The Payment Plan Group delivery exporter records the exact Payments written to each XLSX. After the file is saved
successfully, it changes an exported Payment from `PENDING` to `SENT_TO_FSP` only when the plan is not managed through
Payment Gateway and `delivered_quantity` is empty. The export also updates `status_date`, recalculates the Payment
signature, and writes a Payment change log in the same database transaction as the batch metadata.

A re-export never moves a Payment backwards. `SENT_TO_FSP`, distribution outcomes, errors, cancellations, and
Payment Gateway statuses remain unchanged. A skipped plan or Payment that was not written to the workbook is not
changed.

Existing exports require an explicit one-time backfill because their Payments are still `PENDING`. Run
`hope.one_time_scripts.backfill_sent_to_fsp_for_exported_group_payments.backfill` first in dry-run mode and then with
`dry_run=False`. The script changes eligible Payments to `SENT_TO_FSP` when all these conditions are met:

- the Payment Plan is `ACCEPTED` or `FINISHED` and belongs to a Payment Plan Group;
- the plan has both `export_tag` and `export_file_delivery`;
- the plan is not configured for Payment Gateway and its FSP does not use the API channel;
- the Payment is `PENDING`, has no delivered quantity, and is not conflicted, excluded, or missing a valid wallet.

The new `status_date` is the stored delivery export's creation time. The script runs in batches, recalculates Payment
signatures, and records the previous status, previous status date, export file, and change time in
`Payment.internal_data["sent_to_fsp_group_export_backfill_history"]`. It does not create activity-log records. It does
not change CLOSED or unexported plans, Payment Gateway Payments, delivered quantities, Payment Plan lifecycle statuses,
or money totals. Re-running it is safe because it selects only Payments that are still `PENDING`.

Do not run old and new reconciliation workers at the same time during deployment: old workers expect `PENDING`, while
new workers expect `SENT_TO_FSP`. Before deployment, confirm that no legacy single-plan reconciliation jobs are
active. Pause Payment import/export jobs, deploy the code, run the backfill, and only then resume group imports.

`Payment.PENDING_STATUSES` remains unchanged, so `SENT_TO_FSP` is still treated as unreconciled. Payment Plan
reconciliation state, pending totals, verification eligibility, and money totals therefore do not change. Reports
that show the exact Payment status will move these records from `PENDING` to `SENT_TO_FSP`; status labels and sorting
must display both values correctly.

### Normal mode

After confirming that the Payment belongs to an eligible, non-closed manual Payment Plan, apply these rules from top
to bottom:

| Existing Payment | XLSX quantity | Result |
| --- | --- | --- |
| Any | Empty | Ignore the row |
| Quantity exists | Same quantity | Ignore the row, even if other values differ |
| Quantity exists | Different quantity | Report a conflict and reject the whole file |
| Quantity is empty and status is `SENT_TO_FSP` | Valid value | Reconcile the Payment |
| Quantity is empty and status is not `SENT_TO_FSP` | Any value | Skip as ineligible |

Example: if the Payment already contains `100`, XLSX value `100` is ignored. XLSX value `90` is a conflict; it must not
silently replace `100`.

The importer must compare existing and XLSX quantities before skipping an already-reconciled Payment. Otherwise it
cannot detect the conflict above.

### Override mode

Override requires `override=true` and the new scoped permission
`PM_IMPORT_XLSX_WITH_RECONCILIATION_OVERRIDE`.

Reset is available only in this mode. It applies when the Payment Plan Group XLSX row has an empty/null
`delivered_quantity` and `null_delivery_policy="reset"`. It does not apply in normal mode or to a row with a non-null
quantity. The dedicated Follow-Up Instruction importer remains outside this feature.

Override accepts `SENT_TO_FSP`, `DISTRIBUTION_SUCCESS`, `DISTRIBUTION_PARTIAL`, `NOT_DISTRIBUTED`, and `ERROR`. It
skips `PENDING`, cancelled, force-failed, and unrelated statuses. Including `ERROR` lets an authorised user correct a
previous XLSX `-1` result.

A `FINISHED` Payment Plan is eligible only in override mode. A `CLOSED` plan is never eligible. If the XLSX contains
even one Payment from a CLOSED plan, reject the whole file in either mode.

| XLSX quantity | Empty-value policy | Result |
| --- | --- | --- |
| Any non-empty valid value | Either policy | Overwrite reconciliation values and recompute status |
| Empty | `ignore` | Do nothing |
| Empty | `reset` | Reset the Payment |

Only users with `PM_IMPORT_XLSX_WITH_RECONCILIATION_OVERRIDE` can see these UI controls:

- `This upload will overwrite existing matches`
- `When delivered_quantity is empty`
  - `Reset rows with empty/null delivered_quantity` (default)
  - `Ignore rows with empty/null delivered_quantity`

The API must also reject `override=true` when the user does not hold the scoped permission, even if the request is
submitted without using the UI.

### Payment field contract

After plan and Payment eligibility checks, each row has exactly one action:

| Mode and XLSX value | Existing Payment | Action |
| --- | --- | --- |
| Normal, empty quantity | Any | Preserve |
| Normal, non-empty quantity | Same quantity | Preserve |
| Normal, non-empty quantity | Different non-null quantity | Abort the whole file |
| Normal, valid non-empty quantity | Quantity `None`, status `SENT_TO_FSP` | Apply XLSX values |
| Normal, valid non-empty quantity | Quantity `None`, status other than `SENT_TO_FSP` | Preserve as ineligible |
| Override, empty quantity, policy `ignore` | Eligible | Preserve |
| Override, empty quantity, policy `reset` | Eligible | Reset |
| Override, valid non-empty quantity | Eligible | Apply XLSX values, even when the quantity is unchanged |

`Preserve` means that no Payment field changes and no Payment change log is created. `Abort` means that no Payment in
the file is changed. A CLOSED-plan row always aborts the file. Payment Gateway plans and other ineligible rows are
preserved according to their validation rules.

For optional reconciliation columns, use this rule in both normal first-time reconciliation and non-null override:

- missing header → preserve the stored field;
- present header with a value → store that value; and
- present header with an empty cell → clear the stored field.

Example: if `reference_id` is absent from the workbook, keep `transaction_reference_id = "TX-123"`. If the header is
present but its cell is empty, set `transaction_reference_id = None`.

Apply the following field rules:

| Payment field | Apply XLSX values | Reset | Preserve |
| --- | --- | --- | --- |
| `delivered_quantity` | Store the validated XLSX value; for `-1`, store `None` | `None` | Unchanged |
| `delivered_quantity_usd` | Recalculate from the stored quantity and the Payment Plan exchange-rate logic; for `-1`, store `None` | `None` | Unchanged |
| `status` | Derive from delivered quantity; ignore any XLSX `status` value | `STATUS_SENT_TO_FSP` | Unchanged |
| `status_date` | Set to `timezone.now()` only if the derived status differs from the stored status | Set to `timezone.now()` only if status changes to `SENT_TO_FSP` | Unchanged |
| `delivery_date` | Apply the optional-column rule above | `None` | Unchanged |
| `transaction_reference_id` (`reference_id` header) | Apply the optional-column rule above | `None` | Unchanged |
| `reason_for_unsuccessful_payment` | Apply the optional-column rule above | `None` | Unchanged |
| `additional_collector_name` | Apply the optional-column rule above | `None` | Unchanged |
| `additional_document_type` | Apply the optional-column rule above | `None` | Unchanged |
| `additional_document_number` | Apply the optional-column rule above | `None` | Unchanged |
| `transaction_status_blockchain_link` | Apply the optional-column rule above | `None` | Unchanged |
| Reconciliation `extra_fields` | Update keys represented by custom, non-FSP XLSX headers: store non-empty cells, remove keys for empty cells, and preserve keys whose headers are absent | Clear through `payment.set_extra_fields({})` | Unchanged |
| `fsp_extra_fields` | Always preserve | Always preserve | Unchanged |
| Every other Payment field | Unchanged | Unchanged | Unchanged |

Never replace `payment.extras` directly. Use `set_extra_fields()` with a merged reconciliation dictionary so
`fsp_extra_fields` and unrelated keys are preserved. XLSX columns such as entitlement, `fsp_auth_code`, order/token
numbers, beneficiary information, and collector identity are not reconciliation update fields and must not change.

### Payment Verification cleanup

Apply these rules regardless of the verification record's or verification plan's status:

- Ignored, skipped, or rejected rows: preserve verifications and their grievance tickets.
- First reconciliation: leave verifications unchanged; none are expected yet.
- Override reset (empty quantity with `reset`): delete every linked verification and its grievance tickets.
- Override changes the stored delivered quantity: delete every linked verification and its grievance tickets.
- Override keeps the stored quantity, including changes to other fields only: preserve verifications and tickets.
- An override with no actual changes: preserve verifications and tickets.

Compare the old and new stored quantities, including `None` for the XLSX error marker. A reset still triggers cleanup
when the Payment already has an empty quantity.

Delete grievance tickets linked through either the current verification foreign key or the legacy many-to-many
relation before deleting verifications. Do not delete unrelated grievance tickets or verifications for other Payments.
A legacy ticket shared with a deleted verification is removed as a whole; its other verification records remain.

For every affected verification plan:

- If records remain, recalculate response/outcome counts and set `sample_size` to the remaining record count. Preserve
  the plan's status and lifecycle dates.
- If no records remain, delete the empty plan and its `FileTemp` verification exports. Delete physical export files
  only after commit.
- Existing plan save/delete signals update the Payment Plan's verification summary.

Run all database cleanup in the same transaction as reconciliation. A failed import restores the Payments,
verifications, plans, and grievance tickets. This is deletion, not a reset to pending; it removes saved beneficiary
answers and linked grievance history. Already delivered messages or downloaded files cannot be recalled.

### Payment Plan updates

After any first reconciliation, override, or reset, call `PaymentPlan.update_money_fields()` for every affected plan.
This recalculates:

- `total_entitled_quantity`
- `total_entitled_quantity_usd`
- `total_delivered_quantity`
- `total_delivered_quantity_usd`
- `total_undelivered_quantity`
- `total_undelivered_quantity_usd`

Then apply the Payment Plan lifecycle rule:

| Status before import | State after Payment changes | Payment Plan result |
| --- | --- | --- |
| `ACCEPTED` | Every eligible Payment has a non-pending outcome | Move to `FINISHED`; update plan `status_date` |
| `ACCEPTED` | At least one eligible Payment remains in a pending status | Remain `ACCEPTED`; preserve plan `status_date` |
| `FINISHED` | Plan remains fully reconciled | Remain `FINISHED`; preserve plan `status_date` |
| `FINISHED` | A reset makes the plan no longer fully reconciled | Move to `ACCEPTED`; update plan `status_date` |

Add the `FINISHED → ACCEPTED` transition to `PaymentPlanFlow`. Run the Payment changes, totals, and plan transition in
the same group transaction. Recalculate total cash for households linked to changed Payments. No Payment or Payment
Plan totals, lifecycle status, or household totals are recalculated for a preserved row alone.

This matches the existing operational procedure for manual reconciliation resets in production through the Django
shell: reopen the Payment Plan as `ACCEPTED`, update its `status_date`, and recalculate its money fields. This feature
makes that recovery procedure part of the supported import flow.

## Validation and file result

Accepted delivered quantity values are:

- empty;
- a number greater than or equal to zero; or
- exactly `-1`.

Reject text, dates, booleans, and negative numbers other than `-1`. Keep the existing check that delivered quantity
cannot exceed entitlement.

Duplicate `payment_id` rows, invalid values, quantity conflicts, and Payments belonging to CLOSED plans reject the
whole file with `XlsxError` entries. Nothing is saved.

A valid file containing only ignored or ineligible rows succeeds with zero Payment updates. Save skipped row numbers,
Payment IDs, and reasons in `FileTemp.extras["skipped_rows"]`.

## Transactions and notifications

### Initial upload request (synchronous)

The user waits while the API performs these steps:

1. Open and validate the XLSX inside the existing API `transaction.atomic()`.
2. If validation finds a conflict, return its rows as `XlsxError` with HTTP 400. Do not update Payments or create the
   import Celery task.
3. If validation succeeds, create `FileTemp`, save the group's import state, and use `transaction.on_commit()` to queue
   the background import only after the API transaction commits.

If validation finds a delivered-quantity conflict, send the required conflict email before returning HTTP 400. This
is an inline notification because the conflict is already known, there are no reconciliation writes waiting to
commit, and no background import task is created.

### Background import (asynchronous)

The user does not wait for the Celery worker. It must:

1. Load the stored XLSX and run the same validation again because Payment data may have changed after the initial
   request.
2. Run all plan imports, Payment writes, verification/grievance cleanup, activity logs, and total recalculations
   inside one group `transaction.atomic()`.
3. Roll back the entire file if any plan has a conflict or write failure.
4. If background validation fails, store the errors on the import job and email the original uploader. This error is
   new and was not shown in the successful upload response.
5. After a successful commit, queue the completion email through the existing Mailjet integration.

Send reconciliation emails to the original uploader, including after an administrator restarts an import. Reuse the
existing Mailjet infrastructure; do not add an in-app notification model.

### Validation in both phases

| Phase | Validation |
| --- | --- |
| Initial request | Validate the request options, XLSX structure and headers, Payment IDs, duplicate IDs, plan and Payment eligibility, delivered quantity, entitlement limit, delivery date, and quantity conflicts. |
| Background import | Repeat the same workbook and row validation against the latest database state immediately before writing. The request serializer does not need to run again. |

The Celery group importer repeats validation inside the group transaction and aborts before writing when it finds an
error.

## Activity log

- An ignored row creates no Payment change log because the Payment did not change. Group-level and job-level import
  events may still be recorded.
- First reconciliation, override, and reset must snapshot the Payment before changing it and call
  `bulk_log_payment_changes()` after persistence.
- A non-null override is processed even when its quantity is unchanged. If another tracked field changes, log that
  field difference. If every final value is identical, the bulk logger skips the no-op Payment log.
- Add these reconciliation-owned fields to `Payment.ACTIVITY_LOG_MAPPING` so every changed value is audited:
  - `delivered_quantity_usd`
  - `additional_collector_name`
  - `additional_document_type`
  - `additional_document_number`
  - `transaction_status_blockchain_link`
  - reconciliation `extra_fields`

## Override permission

Implement the override permission using HOPE's existing scoped Role pattern:

1. Add `PM_IMPORT_XLSX_WITH_RECONCILIATION_OVERRIDE = auto()` to `Permissions`.
2. Add the generated account `AlterField` migration for the updated `Role.permissions` choices. Do not add an
   `auth_permission` seed migration.
3. Keep `PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX` as the base action permission.
4. When `override=true`, check the additional permission against `payment_plan_group.cycle.program`:

   ```python
   override_permission = Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION_OVERRIDE
   if override and not request.user.has_perm(override_permission.value, payment_plan_group.cycle.program):
       raise PermissionDenied(detail={"required_permissions": [override_permission.value]})
   ```

## Saved import options

Add `FileTemp.extras` as a JSON field, which requires a core schema migration. Store the original `override` and
`null_delivery_policy` values there when the upload is created. An admin restart must read both values from
`FileTemp.extras` so it repeats the original import mode and policy. Notifications from a restarted import go to
`FileTemp.created_by`, the original uploader, not to the administrator who restarted it.

## Admin rerun

Only the Payment Plan Group admin action is in scope. It must reuse the stored XLSX file and the original options from
`FileTemp.extras`; the administrator does not choose a new override mode or null policy.

The ticket describes rerunning a failed import. The current admin action only restarts an import that is still marked
as running and has an active job: it terminates that job and starts another one. The implementation must add support
for the failed-import state while preserving the existing active-job restart. Keep the administrator as the audit
actor, but send import notifications to the original uploader.

### Legacy single-plan cleanup

The legacy single-plan Celery task and Payment Plan admin restart action are removed. Payment Plan Group upload is the
only supported entry point. The `PaymentPlan.reconciliation_import_file` database field remains only for historical
records and must not be used to start or rerun reconciliation.

## Ticket inaccuracies and contradictions

The following problems remain in the revised ticket.

1. **The existing bug is described inaccurately.** Normally reconciled Payments were already skipped, so equal
   quantities were ignored and conflicts were not overwritten—they were also ignored. Overwriting occurred only for
   inconsistent records with both a delivered quantity and a pending status.

2. **The background-conflict explanation is incorrect.** A synchronous conflict stops the request before a background
   task is created. Therefore, a conflict found by the worker is new and was not shown in the original upload response.
   The implementation stores this error and emails the original uploader.
   _Source: revised ticket — Story 7._

## Resolved business questions

### Payment Verifications

An override reset or a change to delivered quantity deletes all linked verifications and their grievance tickets,
including records in ACTIVE or FINISHED verification plans. Recalculate plans with remaining records and delete empty
plans. First reconciliation and changes to other fields do not change verifications.

_Source: Stefano's follow-up comment — “We reset the PaymentRecord and remove Verification if any”; subsequent agreed
decision rules extend deletion to quantity corrections and require verification-plan cleanup and linked grievance
ticket removal._

### Payments with `ERROR` status

XLSX `-1` sets the Payment to `ERROR`. Allow authorised users to overwrite or reset these Payments so the result can be
corrected through the supported override flow.

_Source: revised ticket — Story 4 and Breaking Changes exclude error statuses from override._

### CLOSED plans in a mixed group

A group may contain both CLOSED and eligible Payment Plans. Load CLOSED-plan Payment IDs only to recognize them during
validation; they are never import targets.

- If the XLSX contains a Payment from a CLOSED plan, return an error for that row and reject the whole file.
- If the XLSX contains only Payments from eligible plans, process it normally. A CLOSED plan merely belonging to the
  group does not block the import.

_Source: Stefano's follow-up comment — if a group file contains rows for a CLOSED Payment Plan, the process must stop._

### Errors found by the background task

The worker validates the file again because Payment data may have changed since upload. If it finds a new validation
error, save the error and email the original uploader so they know the accepted import failed.

_Source: revised ticket — Story 7 says not to email for a background conflict because the user already received the
error from synchronous validation or the admin interface surfaces it._
