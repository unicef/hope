# Vision Integration

## Overview

HOPE integrates with Vision to obtain a Funds Commitment (FC) for an authorized Payment Plan. For eligible Payment
Plans, HOPE sends the plan to Vision automatically, processes the Vision callback, assigns the returned FC group, and
releases the plan for delivery.

The integration uses the Payment Plan's `IN_REVIEW` status while it waits for Vision. A plan cannot proceed to release
or delivery until its FC is assigned successfully.

## Enablement and Eligibility

Vision automation requires both of these flags:

```python
VISION_INTEGRATION_ACTIVE and payment_plan.business_area.vision_integration_active
```

`VISION_INTEGRATION_ACTIVE` enables the integration for the HOPE installation.
`BusinessArea.vision_integration_active` enables it for an individual Business Area.

The standard Vision workflow applies to regular Payment Plans, Top-Ups, and Top-Up Amendments. Follow-Up Payment Plans
do not use Vision because their funds were reserved for the source Payment Plan.

When either flag is disabled:

- Vision automation does not run.
- Vision callbacks are logged without changing FC assignments or Payment Plan status.
- Manual FC assignment, release, Payment Gateway sending, and XLSX export use their standard rules.
- Stored Vision state remains available while the plan waits in `IN_REVIEW` and becomes active again if both flags are
  enabled.
- Completing finance release through the manual flow resets the pending Vision attempt, so enabling the flags later
  does not block delivery with stale Vision state. Vision log entries are retained.

## Automatic Workflow

1. Authorization moves the Payment Plan to `IN_REVIEW`.
2. HOPE queues the Vision request after the database transaction commits.
3. A successful request sets the Vision state to `WAITING_FOR_CALLBACK`.
4. The Vision callback provides the Vision Payment Plan identifier and FC group number.
5. HOPE validates and assigns the FC group.
6. Successful assignment releases the Payment Plan automatically and moves it to `ACCEPTED`.
7. A Payment Gateway plan is sent to Payment Gateway automatically. A non-Payment Gateway plan becomes available for
   the standard XLSX export flow.

While a Vision-managed plan is in `IN_REVIEW`, the regular UI and API block manual FC assignment, manual release, and
manual Payment Gateway sending. XLSX export is unavailable because the plan has not reached `ACCEPTED`.

Enabling Vision for a Business Area does not automatically send Payment Plans that were already in `IN_REVIEW`.
Administrators must send each eligible `NOT_SENT` plan from the Payment Plan's Django admin page. This avoids sending
an existing backlog to Vision as a side effect of enabling a feature flag.

## Sending and Retry

Each request and response is recorded in `payment_plan.internal_data["vision"]["log"]`.

- A successful request sets `WAITING_FOR_CALLBACK` and records that the plan was sent.
- A failed request sets `SEND_FAILED` and stores a sanitized error.
- A failed request can be retried from Django admin or recovered by assigning FC items manually in Django admin.
- The React UI does not provide a Vision send or retry action.
- A request cannot be resent while the plan is in `WAITING_FOR_CALLBACK`.

Request scheduling and processing are idempotent. Concurrent send responses and callbacks merge their Vision data
under a database lock so that one response does not overwrite the other.

## Callback Processing

Vision sends callbacks to:

```text
systems/vision/payment-plan-callback/
```

The callback identifies the Payment Plan by matching `payplan_sno` to `PaymentPlan.unicef_id`. Workflow data is
processed only when:

- both Vision flags are enabled,
- the Payment Plan is in `IN_REVIEW`, and
- its Vision state represents an active request or a previous send, callback, or FC-assignment failure.

Every callback is logged. Callbacks received after a completed release, abort, rejection, or while Vision is disabled
do not change FC assignments or Payment Plan status. Duplicate callbacks do not repeat release or delivery side
effects.

### Callback Outcomes

| Callback result | Vision state | Payment Plan result |
| --- | --- | --- |
| Invalid payload or missing Vision identifier | `CALLBACK_FAILED` | Remains `IN_REVIEW`; no FC changes |
| Plan has no active Vision request | Unchanged | Callback is logged; no workflow changes |
| Vision reports failure | `CALLBACK_FAILED` | Remains `IN_REVIEW`; no FC changes |
| Success without `fc_num` | `FC_MISSING` | Remains `IN_REVIEW`; no FC changes |
| No matching HOPE FC group | `FC_NOT_FOUND` | Remains `IN_REVIEW`; no FC changes |
| More than one group matches | `CALLBACK_FAILED` with `FC_AMBIGUOUS` | Remains `IN_REVIEW`; no FC changes |
| The FC conflicts with another assignment | `CALLBACK_FAILED` with `FC_CONFLICT` | Remains `IN_REVIEW`; no FC changes |
| FC assignment succeeds | `FC_ASSOCIATED`, then `RELEASED` | Moves to `ACCEPTED` and continues to delivery |

An FC assignment failure returns HTTP `400`, status `KO`, and message `FC not found`. A later callback retries
processing from `SEND_FAILED`, `CALLBACK_FAILED`, `FC_MISSING`, or `FC_NOT_FOUND`. A successful callback with a valid
FC can therefore recover the workflow without admin intervention. Callbacks that still cannot assign an FC return the
same `KO` response.

## Funds Commitment Assignment

Vision's `fc_num` identifies a `FundsCommitmentGroup`. Automatic assignment works as follows:

1. HOPE matches `FundsCommitmentGroup.funds_commitment_number` to `fc_num` and scopes the match through the Payment
   Plan's Business Area.
2. Exactly one group must match.
3. Every item under the group is locked and assigned to the Payment Plan in one transaction.
4. Items already assigned to the same Payment Plan are accepted as an idempotent result.
5. Assignment fails without making changes if an item belongs to another Payment Plan or the Payment Plan already has
   items from another group.

Historical item-level assignments remain valid. If a historical FC group is split across multiple Payment Plans, it
can be viewed but cannot be assigned automatically as a complete group.

The standard non-Vision FC flow is item-based. A user can select one or more items from a single FC group. The API
validates that all selected items belong to the same group.

## Admin FC Recovery

Django admin provides recovery when sending fails, a sent plan waits indefinitely, or automatic FC assignment fails.
While both Vision flags remain enabled, an administrator can select an available FC group on the recovery page and
select one or more of its available items. The group and item selection happen on the same page. For `SEND_FAILED` or
`WAITING_FOR_CALLBACK` without a successful-send marker, the page warns that HOPE cannot confirm that Vision
received the Payment Plan.

The recovery action rejects:

- an empty selection,
- items from different FC groups,
- items from a different Business Area, and
- items assigned to another Payment Plan.

The admin page warns that successful recovery releases the Payment Plan automatically and immediately starts Payment
Gateway delivery for a Payment Gateway plan. Recovery uses the same `FC_ASSOCIATED` to `RELEASED` transition as an
automatic callback.

## Automatic Release

Successful FC assignment replaces the normal finance-review count and moves the Payment Plan directly from
`IN_REVIEW` to `ACCEPTED`.

- The Payment Plan creator is recorded as the finance-release actor.
- No release comment is added.
- Standard release side effects, activity logging, exchange-rate processing, and release notification run normally.

`PaymentPlan.created_by` is required and protected from deletion, so the creator remains available as the automatic
release actor.

## Abort and Rejection

Aborting or rejecting a Payment Plan does not wait for Vision. If the plan was already sent, HOPE queues a status
notification to Vision through the same `POST /ps/ezcash/PaymentPlan` endpoint:

- abort sends `ABORTED`,
- rejection sends `REJECTED`.

A notification failure is logged but does not block or roll back the local status change. The local Vision attempt is
reset, allowing a later authorization to start a new attempt. A callback received while the plan is outside
`IN_REVIEW` is logged and ignored.

## Payment Gateway and XLSX Delivery

### Payment Gateway Plans

Successful FC assignment and release start the standard Payment Gateway send flow automatically. The integration
reuses Payment Gateway validation, background processing, error states, and Payment Plan activity logging. Automatic
sending is recorded with the Payment Plan creator as the actor. An admin retry is recorded with the administrator as
the actor.

If Payment Gateway sending fails:

- retry is available in Django admin,
- the React send/retry action remains hidden for the Vision-managed plan, and
- Vision does not introduce an additional automatic retry mechanism.

Non-Vision Payment Plans retain both Django admin retry and the standard React send/retry action.

### Non-Payment Gateway Plans

After successful release, non-Payment Gateway plans use the standard XLSX export flow. Vision does not replace the FSP
or introduce another export format. A plan without an assigned FC remains in `IN_REVIEW` and cannot be exported.

No additional comment is added when sending a plan to Payment Gateway or exporting it for an FSP.

## Vision State and UI

Vision workflow data is stored under `payment_plan.internal_data["vision"]`. Supported states are:

- `NOT_SENT`
- `SEND_FAILED`
- `WAITING_FOR_CALLBACK`
- `CALLBACK_FAILED`
- `FC_MISSING`
- `FC_NOT_FOUND`
- `FC_ASSOCIATED`
- `RELEASED`

Failure details use structured error codes, including `FC_AMBIGUOUS` and `FC_CONFLICT`.

The Payment Plan detail API exposes Vision enablement, workflow status, Vision identifier, FC number, and user-safe
failure details. The React Payment Plan page displays Vision progress and blocking reasons. For Vision-managed plans,
it does not display actions for manual FC assignment, manual release, manual Vision sending, or manual Payment Gateway
sending.

## Notifications

Successful FC assignment and automatic release use the standard release notification. The Payment Plan creator is the
recorded action user. Vision send failures and FC assignment failures do not send a separate creator notification.

Callback idempotency prevents duplicate callbacks from creating repeated notifications.
