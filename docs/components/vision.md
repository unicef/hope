# Vision Integration

## Ownership

Vision works with a Payment Plan Group. HOPE sends one request for an authorized group, and the callback's
`payplanSno` is `PaymentPlanGroup.unicef_id`. The group owns the Vision status, Vision ID, request and callback log,
errors, and Funds Commitment (FC) headers. Its member Payment Plans retain their normal payment statuses and delivery
processing, but have no Vision send or recovery actions.

Group Vision data is stored in `PaymentPlanGroup.internal_data["vision"]`. Existing Vision data in
`PaymentPlan.internal_data` is left untouched and is not read by the new workflow. There is no backfill of old plan
Vision state into groups.

## Eligibility

Automation requires the `VISION_INTEGRATION_ACTIVE` flag and `BusinessArea.vision_integration_active`. Regular,
Top-Up, and Top-Up Amendment groups are eligible. Follow-Up groups reuse funds reserved for their source group and do
not request a new FC from Vision. Follow-Up Instruction plans have no group and do not use this workflow.

If either flag is disabled, callbacks are logged without changing FC assignments or group status. Manual group FC
assignment and finance release use their normal rules. Completing manual finance release resets an active group
Vision attempt while retaining its log.

## Request

After group authorization moves the group and its plans to `IN_REVIEW`, HOPE queues one Vision request on transaction
commit. The payload uses the group's UNICEF ID as `payplanSno`, its currency and FSP, and sums the plans'
`total_entitled_quantity` and `total_entitled_quantity_usd` as `authAmt` and `authAmtUsd`. `exchangeRate` is currently
`null`; it will come from the group when the exchange rate moves there.

Successful sending records `WAITING_FOR_CALLBACK`. Failure records `SEND_FAILED`. Sending and retry are available in
the Payment Plan Group's Django admin page. The React UI shows status but has no send or retry action. Send responses
and callbacks update group Vision data under a database lock so a late response cannot overwrite a newer callback.

## Callback and FC assignment

Vision calls `systems/vision/payment-plan-callback/`. HOPE locks the group identified by `payplanSno`, records the
callback payload and response, and processes it only for an active group in `IN_REVIEW`. The first successful callback
without FC numbers records `PP_CREATED`; a later successful callback can provide one or more FC numbers. Failed
callbacks record `CALLBACK_FAILED`.

Each FC number must match a header with an item in the group's Business Area. All matching headers are assigned to
the group. A missing header records `FC_NOT_FOUND`, leaves the group in review, and returns a failed callback response.
A corrected callback can complete a recoverable attempt. Callbacks after release, rejection, or abort are logged and
do not repeat release or delivery.

The callback acknowledgement contains `status`, `messageId`, `payplanSno`, and `message`. Unknown group IDs return
HTTP 404. Invalid payloads and FC assignment failures return HTTP 400.

## Release and delivery

Successful FC assignment records one group finance-release approval. HOPE accepts the group and every member plan in
one transaction, sends one group release notification, and updates the plans' exchange-rate dependent payments. Each
eligible Payment Gateway plan is dispatched after the group has been accepted. Other plans use the standard group
delivery XLSX export.

If automatic FC assignment cannot finish, a group admin can assign one or more eligible FC headers and complete the
same release flow. The recovery page warns when HOPE cannot confirm that Vision received the group request.

Aborting or rejecting a group resets its active Vision attempt and sends one `ABORTED` or `REJECTED` status notification
to Vision if the group request was received. Notification failure does not roll back the local status change.

## User interface

The Payment Plan Group detail API and page show Vision status, Vision ID, FC numbers, errors, and assigned FC headers.
They also provide manual FC assignment when the group is not managed by Vision. Individual Payment Plan detail pages
do not show Vision actions or state. Their normal payment and Payment Gateway details remain available.

Vision statuses are `NOT_SENT`, `SEND_FAILED`, `WAITING_FOR_CALLBACK`, `PP_CREATED`, `CALLBACK_FAILED`,
`FC_NOT_FOUND`, `FC_ASSOCIATED`, and `RELEASED`.
