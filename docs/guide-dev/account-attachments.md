---
title: Account Attachments
tags:
    - Payments
    - Population
---

# Account Attachments

An **Account Attachment** is a file attached to one of an individual's payment accounts. Only one thing creates them today: the **wallet number image** from the Ukraine USDC registration. The model is `AccountAttachment`, in `src/hope/models/account_attachment.py` under `app_label = "payment"`.

| Field | Notes |
|---|---|
| `account` | FK to `Account`, `CASCADE` |
| `title` | free text, optional — falls back to the file name in `__str__` |
| `file` | `FileField`, stored under `{program_start_year}/ba/{business_area_id}/programs/{program_id}/individuals/{individual_id}/accounts/{account_id}/` (`account_attachment_path`) |
| `uploaded_at` | `auto_now_add`, also the `ordering` key |
| `created_by` | FK to user, `SET_NULL`. Only the REST upload fills it in — the RDI import, the Aurora parser and the one-time script leave it null |

## Limits

Two limits, both class constants on the model, both enforced in `Model.clean()`, which `save()` calls unconditionally:

- `FILE_LIMIT = 10` attachments per account
- `FILE_SIZE_LIMIT = 10 MB` per file

The two behave differently on update, on purpose:

- **Size is re-checked on every save.** The file stays editable in the Django admin, so an update can swap a small file for an oversized one.
- **The count is checked only when adding** (`self._state.adding`), so attachments on a full account can still be edited.

A third rule, the allowed extension list (`pdf`, `xlsx`, `jpg`, `jpeg`, `png`), is enforced only in the API serializers (`AccountAttachmentUploadSerializer` and, for the CW push, `AccountAttachmentLaxSerializer`). That is a UI rule, not a data invariant, so the model ignores it and the admin can store anything.

## REST API

Two nested routers are registered in `src/hope/apps/household/api/urls.py`, under the existing per-program `individuals` route:

```
/api/rest/business-areas/{business_area_slug}/programs/{program_code}
    /individuals/{individual_pk}/accounts/{account_pk}/attachments/
```

| Endpoint | Method | Purpose |
|---|---|---|
| `.../individuals/{individual_pk}/accounts/` | `GET` | list an individual's accounts, attachments prefetched |
| `.../accounts/{account_pk}/` | `GET` | one account |
| `.../accounts/{account_pk}/attachments/` | `POST` | upload (multipart: `file`, optional `title`) |
| `.../attachments/{file_id}/` | `DELETE` | remove |
| `.../attachments/{file_id}/download/` | `GET` | stream as `attachment` |

Both viewsets (`AccountViewSet`, `AccountAttachmentViewSet` in `src/hope/apps/payment/api/views.py`) are gated by `POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION`.

Attachments also come back read-only on the individual detail payload, through `AccountSerializer.attachments` (`src/hope/apps/household/api/serializers/individual.py`).

### Scoping

Both viewsets use `ProgramVisibilityMixin`, so the queryset is cut down to the caller's program and, when the caller's partner has area limits, to the admin areas they may see. `AccountAttachmentViewSet` declares those paths through `account__individual__household__admin1..3`.

`get_queryset()` is not enough on its own. `CreateModelMixin.create()` never calls it, so an upload would otherwise skip the filtering that `DELETE` and `download` get for free. The account is therefore resolved in `get_serializer_context()` against `_visible_accounts()`, which repeats the program filter and the area-limit filter explicitly, and the serializer takes the account from the context rather than from the request body.

## Import paths

### Aurora — Ukraine USDC

`UkraineUSDCRegistrationService` receives two base64 images per record. `wallet_num_image_i_f` becomes an attachment on the wallet account; `id_wallet_image_i_f` stays an individual flex field (`INDIVIDUAL_IMAGE_FLEX_FIELDS`).

The size check for the wallet image is explicit in the service rather than left to the model, so the record fails with a field-keyed `ValidationError` the operator can read.

### Existing data

Some records were imported with the wallet image written to the individual's `wallet_num_image_i_f` flex field. `src/hope/one_time_scripts/migrate_wallet_images_to_account_attachments.py` relocates those: for each such individual it copies the file through the model field, so the copy lands under the structured upload path, creates the attachment on that individual's `transfer_to_digital_wallet` account, and drops the flex key — the copy and the flex-key deletion happen in one transaction.

Run it from the Django shell:

```python
from hope.one_time_scripts.migrate_wallet_images_to_account_attachments import (
    migrate_wallet_images_to_account_attachments,
)

migrate_wallet_images_to_account_attachments()
```

It is safe to re-run and it never stops on a bad record:

- No wallet account, or the source file is missing from storage → skipped, flex field left untouched.
- Any other failure → the copied file is deleted, the error is printed, the run continues.
- The **source file is never deleted**. Only the flex key goes. Rolling back means restoring the key, not restoring the file.

It prints a `migrated / skipped / failed` tally at the end.

### RDI API upload

`AccountSerializerUpload` (`src/hope/api/endpoints/rdi/upload.py`) accepts an optional `attachments` array on each account of the `rdi-upload`, `rdi-push` and `rdi-push-lax` endpoints:

```json
{
  "accounts": [
    {
      "type": "bank",
      "number": "123456",
      "attachments": [
        {"title": "Bank statement", "file": "<base64>"}
      ]
    }
  ]
}
```

`file` is base64, the same encoding those endpoints use for photos and documents. One payload can carry any number of attachments per account, so their count is checked against `FILE_LIMIT` up front. The size is checked **before decoding**: base64 packs 3 bytes into 4 characters, so `len(value) * 3 // 4` is enough to reject an oversized blob without ever holding the decoded image in memory. The model then enforces the exact limit once the file exists.

`AccountMixin.save_account` (`src/hope/api/endpoints/rdi/mixin.py`) pops `attachments` off the payload, creates the `PendingAccount`, and writes one `AccountAttachment` per entry, reusing `PhotoMixin.get_photo` to turn the base64 into a file.

### CW push

`rdi-push-lax-individuals` and `rdi-push-people`, the endpoints Country Workspace calls, take attachments as **storage file names**, not base64. CW writes the file to the media container it shares with HOPE and sends its name. HOPE stores that name and never copies the file, so it stays at CW's path, not at `account_attachment_path`. CW-pushed images work the same way.

```json
{
  "type": "bank",
  "number": "123456",
  "attachments": [
    {"file": "2026/afghanistan/ab12/CW_ind_42_attachment_9f0c.pdf", "title": "contract.pdf"}
  ]
}
```

Both endpoints share `AccountLaxSerializer` (`src/hope/api/endpoints/rdi/lax.py`). Its optional `attachments` field is `AccountAttachmentLaxSerializer`:

- `file` is a `StoredFileField` (`src/hope/api/endpoints/rdi/stored_images.py`), which runs the same checks as `StoredImageField`: a plain relative name, under the RDI's `<year>/<business area slug>/<program code>/` directory, that exists in storage. The directory check stops a token from referencing files of another business area or program. The allowed extensions are `ATTACHMENT_ALLOWED_EXTENSIONS`.
- The file name also has to start with `CW_` (`CW_FILE_NAME_PREFIX`), the prefix CW gives every file it writes for HOPE. HOPE keeps its own files (exports, supporting documents, imports) in the same directory, so without the prefix a token could attach one of them and expose it through the attachment download. The prefix is checked before the storage is asked, so the error doesn't reveal whether a HOPE file exists.
- `title` is optional, may be blank and defaults to `""`.
- Size (`FILE_SIZE_LIMIT`, read with `default_storage.size`) and count (`FILE_LIMIT`) are checked in the serializer too. A bad attachment comes back as a field error: per record in `results` on lax individuals, a 400 for the batch on push people.

`rdi-push-lax-households` carries no accounts. A re-push with the same `originating_id` deletes the old individual, and the delete cascades to its attachment rows. HOPE never deletes the files, so the new rows can point at the same names.

## Django admin

`AccountAttachmentInline` is a tabular inline on `AccountAdmin`, with `uploaded_at` and `created_by` read-only and a `View` link per row. There is also a standalone `AccountAttachmentAdmin` (`src/hope/admin/account_attachment.py`) — list, search by title, filter by account type, `date_hierarchy` on `uploaded_at`.

The admin skips the extension allow-list (that rule lives in the API serializer) but **not** the size and count limits, which come from `Model.clean()`.

## What the user sees

The frontend only displays attachments — there is no upload or delete button. On the individual details page, the Accounts card renders each attachment next to the account's data fields (`src/frontend/src/components/population/IndividualAccounts.tsx`). Images (`jpg`, `jpeg`, `png`) open in the existing `PhotoModal`; anything else renders as a download link. The label is the attachment's title, or "Attachment" when the title is empty.

For a USDC beneficiary that means one tile labelled *Wallet number image*, under the wallet account.

The card is only rendered for users holding `POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION`, the same permission that guards the API.

## Migrations

- `payment/0075_migration.py` — creates the table. Additive only: a new model, two nullable-safe FKs, no change to `Account` or `Individual`.
- The flex-field cleanup is **not** a migration. It is the one-time script above, run deliberately after deploy.
