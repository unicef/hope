# Timezone configuration

HOPE stores datetime values in UTC. Users and Business Areas store IANA timezone identifiers, which are used to
display those values in the appropriate local timezone. The stored datetime values and REST API datetime responses
remain in UTC.

Examples of valid IANA identifiers include `UTC`, `Africa/Nairobi`, `America/New_York`, and `Europe/London`.
Identifiers are validated by `django-timezone-field` against the installed timezone database. Consumers should use
the API choice list and prefer stable region/city identifiers; a numeric offset such as `+02:00` is not a substitute
for a timezone because it does not contain daylight-saving rules.

## Business Area timezone

Every persisted Business Area has a non-empty `timezone`, which is visible and editable in Django admin. When a new
Business Area is saved without an explicit timezone, HOPE initializes it from `office_country.iso_code2`. The first
IANA timezone in the country mapping is used, with UTC as the fallback when the country is missing or unmapped. An
explicitly selected timezone takes precedence.

The custom **Create Business Office** form follows the same rule. The new Business Office copies its parent's
`office_country` and derives its timezone from that country when no explicit timezone is selected. Changing an
existing Business Area's `office_country` does not overwrite its current timezone.

Existing Business Areas are initialized during migration using the same first timezone mapped to
`office_country.iso_code2`, with UTC used when the country is missing or unmapped. This is a provisional migration
value: administrators must review migrated Business Areas, especially in multi-timezone countries, and explicitly
select the correct operational value. Country-derived values for newly created Business Areas in multi-timezone
countries require the same review.

## User timezone

`User.timezone` is an optional personal preference:

- An IANA identifier means that the User explicitly selected that timezone.
- `UTC` means that the User explicitly selected UTC.
- `null` means that the User has no personal preference and inherits from the current Business Area.

Administrators can edit the field in the User's **Personal info** section in Django admin. An authenticated User can
also update only their own preference through the scoped REST endpoint described below.

A User can work in several Business Areas. HOPE therefore never selects a fallback Business Area from the User's
role assignments. The current Business Area must be supplied explicitly when resolving the effective timezone.

## Effective timezone

The effective timezone is the timezone that applies to a particular human-facing context. It is resolved as follows:

| Context | Resolution order |
| --- | --- |
| Business Area-scoped User interface | User preference, current Business Area, UTC |
| Notification | Recipient User, related Business Area, UTC |
| User-requested single-Business-Area output | Requesting User, current Business Area, UTC |
| Unattended Business-Area-specific human output | Business Area, UTC |
| Global or multi-Business-Area output | UTC |
| Celery trigger or scheduled-task window | UTC |

For example, if a User has no personal preference and the current Business Area uses `Africa/Nairobi`, both
`timezone: null` and `effective_timezone: "Africa/Nairobi"` are returned for that scoped profile. If the User then
selects `Europe/London`, that personal preference becomes effective in every Business Area context.

## REST API

### Reading timezone values

The standalone Business Area endpoints expose the stored Business Area timezone as `timezone: string`.

The scoped User profile exposes the stored preference as `timezone: string | null` and also exposes
`effective_timezone: string`, resolved against the Business Area in the URL. User lists, program-user responses,
shared nested User representations, and Business Areas nested in the profile do not expose timezone fields. The
frontend reads the effective value once from the scoped profile and shares it through its authenticated context:

```http
GET /api/rest/business-areas/{business_area_slug}/users/profile/
```

Example profile fields:

```json
{
  "timezone": null,
  "effective_timezone": "Africa/Nairobi",
  "business_areas": [
    {
      "name": "Kenya",
      "slug": "kenya"
    }
  ]
}
```

The nested Business Area identifies the source of an inherited preference for display purposes;
`effective_timezone` contains the value that clients use for datetime conversion.

Business Area REST resources are read-only. Administrators change their timezone through Django admin.

### Updating the User preference

An authenticated User updates their own preference with:

```http
PATCH /api/rest/business-areas/{business_area_slug}/users/profile-timezone/
Content-Type: application/json
```

To select a timezone:

```json
{
  "timezone": "Europe/Warsaw"
}
```

To clear the preference and inherit from the current Business Area:

```json
{
  "timezone": null
}
```

The response contains both the stored preference and the newly resolved effective timezone:

```json
{
  "timezone": "Europe/Warsaw",
  "effective_timezone": "Europe/Warsaw"
}
```

The endpoint updates only `timezone`; no other User field is writable through it. An invalid or unknown identifier
returns HTTP 400 with a field-level validation error. Saving the preference invalidates the User's cached profile
after the database transaction commits.

### Listing accepted timezone identifiers

Clients can load the validated, alphabetically sorted choice list from:

```http
GET /api/rest/business-areas/{business_area_slug}/users/timezone-choices/
```

The response uses the standard HOPE choice shape:

```json
[
  {
    "name": "Europe/London",
    "value": "Europe/London"
  },
  {
    "name": "Europe/Warsaw",
    "value": "Europe/Warsaw"
  }
]
```

Clients should load this large list only when it is needed instead of including it in every profile request.

## REST datetime values

REST datetime fields remain UTC. They are serialized with a trailing `Z`, which identifies UTC:

```json
{
  "created_at": "2026-08-24T10:30:00Z"
}
```

The API does not replace this value with a User-local or Business-Area-local timestamp. A client displays it by:

1. Parsing the REST value as a UTC instant.
2. Selecting `effective_timezone` for the current scoped context.
3. Converting the instant with an IANA-aware library such as the browser `Intl.DateTimeFormat` API.
4. Showing the IANA identifier with the rendered value when the timezone context matters.

For example, `2026-08-24T10:30:00Z` displayed in `Europe/Warsaw` is `24 August 2026 12:30 PM
(Europe/Warsaw)` while daylight-saving time is active. The source instant remains unchanged.

True date-only values such as `2026-08-24` have no time or timezone and must not be converted. Converting a date-only
value as though it were midnight UTC can incorrectly move it to the previous or next calendar day.

Some date-only values remain backed by legacy datetime database columns. Their human-facing and REST contracts are
still date-only: HOPE converts the stored value to its UTC calendar date and returns `YYYY-MM-DD`. Clients must not
localize these fields:

- Payment `delivery_date`.
- Payment Plan `start_date` and `end_date`.
- Document `issuance_date` and `expiry_date`.
- Sanction-list individual `listed_on`.

New Payment delivery dates are stored as midnight UTC. The other legacy columns retain their existing storage and
write behavior; the explicit date-only conversion occurs at their approved presentation boundaries.

## Human-facing notifications and outputs

Human-facing timezone-aware values use a stable IANA identifier rather than only an ambiguous abbreviation. The
backend human-readable format is:

```text
24 August 2026 12:30 PM (Europe/Warsaw)
```

Payment Plan and Periodic Data Update email notifications resolve each recipient's effective timezone. Recipients
with the same effective timezone are grouped so that one correctly localized message can be rendered for the group.
The creation and action timestamps in those emails are converted to that timezone and include its IANA identifier.

For a human-facing report or document concerning one Business Area, use the requesting User's preference, then the
Business Area timezone, then UTC. Global or multi-Business-Area outputs remain UTC and must state that timezone
explicitly.

The User XLSX export contains a `TIMEZONE` column with the stored personal preference. A blank value means that the
User inherits the relevant Business Area timezone; the export does not replace that blank value with one arbitrary
effective timezone.

## UTC boundaries

The timezone settings affect human-facing presentation. They do not change these UTC contracts:

- REST and OpenAPI datetime values.
- Datetime storage and audit/event storage.
- Celery schedules, triggers, and internal scheduled-task date windows.
- FSP and payment-gateway interchange files.
- Partner-facing machine imports and exports.
- Round-trip files containing timestamps that are parsed again on import.
- Global processing and multi-Business-Area output.

Changing a Business Area timezone does not automatically change business-rule deadlines, date filters, or the day
boundaries used by scheduled processing. Code that intentionally implements a Business-Area-local calendar rule must
receive that Business Area explicitly and calculate its local date from an aware instant.

Timezone conversion requires aware datetime values. Callers must attach the correct UTC or source offset before
conversion; naive datetime values are rejected instead of being assigned an assumed timezone.

## Daylight-saving time

Timezone conversion must use the complete IANA identifier, not a fixed UTC offset. IANA rules account for seasonal
offset changes and daylight-saving transitions. `Europe/Warsaw`, for example, cannot be represented correctly for a
whole year by a fixed `UTC+1` or `UTC+2` preference.

HOPE's shared timezone helpers resolve effective timezones, convert aware datetime values, format human-readable
timestamps, and calculate a scoped local date. They do not globally activate a User or Business Area timezone for a
request because doing so could change the UTC REST serialization contract.

## Operational checklist

When creating or maintaining a Business Area:

1. Select the `office_country`; select an explicit timezone when the derived country default is not appropriate.
2. Save the Business Area and verify that the timezone column is populated.
3. Update the timezone manually if the Business Area's operational location changes.

When diagnosing a User's displayed timezone:

1. Check the stored `User.timezone` value.
2. Check the current Business Area's stored timezone.
3. Check `effective_timezone` in the scoped profile response.
4. Confirm that the REST datetime was parsed as UTC before display conversion.
5. Confirm that a date-only field was not passed through datetime conversion.
