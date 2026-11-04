# Vision Integration

## Ownership

Vision works with a Payment Plan. HOPE sends one request for an authorized payment plan, and the callback's
`payplanSno` is `PaymentPlan.unicef_id`. The payment plan owns the Vision status, Vision ID, request and callback log,
errors, and Funds Commitment (FC) headers. Its member Payment Lists retain their normal payment statuses and delivery
processing, but have no Vision send or recovery actions.

Payment plan Vision data is stored in `PaymentPlan.internal_data["vision"]`. Existing Vision data in
`PaymentPlan.internal_data` is left untouched and is not read by the new workflow. There is no backfill of old payment list
Vision state into payment plans.

## Enablement and eligibility

Automation requires the `VISION_INTEGRATION_ACTIVE` flag and `BusinessArea.vision_integration_active`. Regular,
Top-Up, and Top-Up Amendment payment plans are eligible. Follow-Up payment plans reuse funds reserved for their source payment plan and do
not request a new FC from Vision. Follow-Up Instruction payment lists have no payment plan and do not use this workflow.

If either flag is disabled, callbacks are logged without changing FC assignments or payment plan status. Manual payment plan FC
assignment and finance release use their normal rules. Completing manual finance release resets an active payment plan
Vision attempt while retaining its log.

Enabling Vision for a Business Area does not automatically send payment plans already in `IN_REVIEW`. An administrator must
send each eligible `NOT_SENT` payment plan from the payment plan's Django admin page. This prevents a feature flag change from
sending an existing backlog to Vision.

A payment plan accepted while Vision was disabled can still have `NOT_SENT` status. It remains eligible for normal manual
Payment Gateway sending or XLSX export. A payment plan that has started a Vision attempt is excluded from the manual payment plan
Payment Gateway action while both flags are enabled; a failed automatic Gateway send is retried on the individual
Payment List's Django admin page. Follow-Up payment lists remain eligible for the manual payment plan Gateway action because they
do not request a new FC from Vision.

## Automatic workflow

1. Payment Plan authorization moves the payment plan and its payment lists to `IN_REVIEW`.
2. HOPE queues one Vision request after the database transaction commits.
3. Vision acknowledges creation with a callback without FC numbers; HOPE records `PP_CREATED`.
4. Vision sends a later callback with one or more FC numbers; HOPE validates and assigns all matching headers.
5. HOPE records one payment plan finance release, accepts the payment plan and its payment lists, and starts eligible delivery work.

While a payment plan is managed by Vision in `IN_REVIEW`, the normal payment plan UI and API block manual FC assignment and
finance release. Gateway delivery and XLSX export require an accepted payment plan.

## Request and retry

The request payload uses the payment plan's UNICEF ID as `payplanSno`, its currency and FSP, and sums the payment lists'
`total_entitled_quantity` and `total_entitled_quantity_usd` as `authAmt` and `authAmtUsd`. `exchangeRate` is currently
`null`; it will come from the payment plan when the exchange rate moves there.

| Payload field | Source |
| --- | --- |
| `payplanSno` | `PaymentPlan.unicef_id`; also used to identify the payment plan in callbacks |
| `payplanDesc` | Payment Plan name |
| `businessArea` | Payment Plan's Programme Business Area code |
| `vendorNumber`, `headVendor` | Payment Plan's Financial Service Provider |
| `currency` | Payment Plan currency's Vision code |
| `authAmt`, `authAmtUsd` | Sums of member payment lists' entitled amounts |
| `exchangeRate` | `null` until exchange rate is moved to the payment plan |

Successful sending records `WAITING_FOR_CALLBACK`. Failure records `SEND_FAILED`. Sending and retry are available in
the Payment Plan's Django admin page. The React UI shows status but has no send or retry action. Send responses
and callbacks update payment plan Vision data under a database lock so a late response cannot overwrite a newer callback.

Each request and response is logged under `PaymentPlan.internal_data["vision"]["log"]`. A failed request stores
an error and can be retried from admin when the payment plan is still eligible. HOPE does not resend a payment plan already marked
as sent to Vision. An admin can instead recover an active failed or stalled attempt by assigning eligible FC headers.

The send task locks and checks the payment plan before sending. A late HTTP result cannot restore an attempt after abort,
rejection, or release, or overwrite a later callback status.

## Callback processing

Vision calls `systems/vision/payment-plan-callback/`. HOPE locks the payment plan identified by `payplanSno`, records the
callback payload and response, and processes it only for an active payment plan in `IN_REVIEW`. The first successful callback
without FC numbers records `PP_CREATED`; a later successful callback can provide one or more FC numbers. Failed
callbacks record `CALLBACK_FAILED`.

Each FC number must match a header with an item in the payment plan's Business Area. All matching headers are assigned to
the payment plan. A missing header records `FC_NOT_FOUND`, leaves the payment plan in review, and returns a failed callback response.
A corrected callback can complete a recoverable attempt. Callbacks after release, rejection, or abort are logged and
do not repeat release or delivery.

The callback acknowledgement contains `status`, `messageId`, `payplanSno`, and `message`. Unknown payment plan IDs return
HTTP 404. Invalid payloads and FC assignment failures return HTTP 400.

| Callback result | Payment Plan Vision state | HTTP result and workflow effect |
| --- | --- | --- |
| Invalid payload | Unchanged | `400`; no FC changes |
| Unknown `payplanSno` | No payment plan found | `404`; no FC changes |
| Missing `vision_payplanSno` during an active wait | `CALLBACK_FAILED` | `400`; payment plan remains `IN_REVIEW` |
| No active Vision request | Unchanged | Callback logged; no workflow changes |
| `SUCCESS` without FC numbers | `PP_CREATED` | `200`; waits for the FC callback |
| Vision reports failure | `CALLBACK_FAILED` | `200` acknowledgement; payment plan remains `IN_REVIEW` |
| Any FC number lacks an eligible header | `FC_NOT_FOUND` | `400`; payment plan remains `IN_REVIEW` |
| All FC numbers match eligible headers | `FC_ASSOCIATED`, then `RELEASED` | `200`; payment plan and payment lists become `ACCEPTED` |

The callback's `vision_payplanSno` is Vision's identifier for the payment plan. For an active request, a callback carrying
that identifier confirms that Vision received the payment plan, even if the original send response was lost or Vision reports
an error. Every callback associated with a known payment plan is logged with its receipt time, payload, and response.
Repeated creation acknowledgements do not replace later FC results. Duplicate callbacks after release do not repeat
approval, notifications, or delivery.

Failed attempts can be completed by a corrected callback from `SEND_FAILED`, `WAITING_FOR_CALLBACK`, `PP_CREATED`,
`CALLBACK_FAILED`, or `FC_NOT_FOUND`. An unsolicited callback for `NOT_SENT` does not start a Vision workflow.

## Funds Commitment assignment

Vision can return multiple `fc_numbers`. Each number must resolve to a `FundsCommitmentHeader` with at least one
`FundsCommitmentItem` belonging to the payment plan's Business Area. HOPE assigns every matching header to the payment plan; one
header can be associated with multiple payment plans. Business Area, WBS, and grant remain item-level attributes. If any
number does not match an eligible header, automatic assignment fails without releasing the payment plan.

The standard non-Vision flow also assigns one or more eligible headers to the payment plan. Follow-Up payment plans reuse funds
reserved for their source payment plan. Follow-Up Instruction children have no payment plan and keep their own approval workflow.

## Admin FC recovery

Django admin offers recovery when sending fails, a payment plan waits for a callback, or automatic FC assignment fails.
Recovery requires the payment plan and all its payment lists to remain in `IN_REVIEW`, both Vision flags to be active, and the payment plan
to have a recoverable Vision state. The admin can select one or more headers; empty or ineligible selections fail
validation. Recovery adds the selected headers and runs the same release flow as a successful callback.

When HOPE cannot confirm that Vision received the request, the recovery page warns the administrator. A callback
with a Vision identifier confirms receipt even when the original request response was lost. Successful recovery
releases the payment plan and may immediately queue Payment Gateway delivery for eligible payment lists.

## Automatic release

Successful FC assignment records one payment plan finance-release approval. HOPE accepts the payment plan and every member payment list in
one transaction, sends one payment plan release notification, and updates the payment lists' exchange-rate dependent payments. Each
eligible Payment Gateway payment list is dispatched after the payment plan has been accepted. Other payment lists use the standard payment plan
delivery XLSX export.

The payment plan creator, or the first payment list's creator when the payment plan has no creator, is recorded as the finance-release actor.
No release comment is added. A second callback after release does not create another approval or notification.

## Payment Gateway and XLSX delivery

Vision release uses the standard Payment Gateway send flow for each eligible payment list. It retains the usual validation,
background processing, error state, and payment list activity log. If automatic sending fails, retry is available in Django
admin on the affected Payment List. The React payment plan send action excludes payment lists handled by an active Vision workflow,
and Vision adds no automatic Gateway retry.

Plans using an FSP's XLSX delivery route use the normal payment plan payment-list export after release. A payment plan still in
`IN_REVIEW` cannot export a delivery list. Vision does not replace the FSP or introduce another export format.

## Abort and rejection

Aborting or rejecting a payment plan resets its active Vision attempt and sends one `ABORTED` or `REJECTED` status notification
to Vision if the payment plan request was received. Notification failure does not roll back the local status change.

The notification uses the same `POST /ps/ezcash/PaymentPlan` endpoint as creation. Resetting an attempt clears its
active status, sent marker, Vision ID, and FC numbers, but retains the log. Callbacks received after abort or rejection
are logged and do not alter FC assignments or payment plan status.

## Vision state and user interface

The Payment Plan detail API and page show Vision status, Vision ID, FC numbers, errors, and assigned FC headers.
They also provide manual FC assignment when the payment plan is not managed by Vision. Individual Payment List detail pages
do not show Vision actions or state. Their normal payment and Payment Gateway details remain available.

Vision statuses are `NOT_SENT`, `SEND_FAILED`, `WAITING_FOR_CALLBACK`, `PP_CREATED`, `CALLBACK_FAILED`,
`FC_NOT_FOUND`, `FC_ASSOCIATED`, and `RELEASED`.

Failure details use structured error codes where applicable. Send failures and FC assignment failures do not send a
separate creator notification; successful payment plan release uses the standard release notification.
