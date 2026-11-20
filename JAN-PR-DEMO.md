# Collisions & Merge — DEMO

Source lines refer to `develop` @ `f9109a5938`.

## Glossary

- **Identification key** — external ID of a household or individual, used to tell whether the same record came back.
- **Collision** — an incoming household has the same identification key as a household already in the population.
- **Collision-merge** — copy the incoming data onto the existing household, then delete the incoming copy.
- **Withdraw** — a member missing from the incoming household is withdrawn, not deleted, and their documents are invalidated.
- **Sanction check** — compare incoming individuals with sanction lists and flag matches with a ticket.
- **Dedup ticket** — grievance ticket asking a person to decide whether two individuals are the same.
- **Batch statistics** — per-RDI counts of unique and duplicate individuals, shown before and after the merge.

## API Ingestion paths

API endpoints that resolve collisions at upload time (prefix `/api/rest/<business_area>/`):

| Endpoint | Location | Comment |
|---|---|---|
| `POST rdi/upload/` | `src/hope/api/endpoints/rdi/upload.py:349` | One request carries RDI, HHs and members. |
| `POST rdi/<rdi>/push/` | `src/hope/api/endpoints/rdi/base.py:116` | RDI already exists in HOPE. Request carries HHs with nested INDs. |
| `POST rdi/<rdi>/push/lax/households/` | `src/hope/api/endpoints/rdi/lax.py:626` | RDI already exists in HOPE. Individuals already pushed as pending. Request carries HHs and IND ids to connect everything using HHs. |

### Problem

All listed paths ends up in

```python
class HouseholdUploadMixin(DocumentMixin, AccountMixin, PhotoMixin):
    def _manage_collision(...) -> str | None:
        ...
```

```mermaid
flowchart TD
    A["Incoming HH"] --> B{collides?}
    B -->|N| R["return None"]
    B -->|Y| U["UPDATE OLD HH with INCOMING HH scalar values"]
```

**Important: `_manage_collision` updates ONLY HHs scalar values.**


### How this impacts listed ingestion paths?

**POST rdi/upload/ (UploadRDIView)**

```mermaid
flowchart TD
    A["POST rdi/upload/"] --> B["RDINestedSerializer.save()<br/>creates RDI"]
    B --> C["save_households()<br/>= HouseholdUploadMixin.save_households()"]
    subgraph LOOP["for each incoming HH"]
        D["build PendingHH (in memory)"] --> E["_manage_collision"]
        E --> F{collides?}
        F -->|N| G["hh.save() + save_member()"]
        F -->|Y| H["continue<br/>hh.save() and save_member() skipped"]
    end
    C --> D
```

Result:
1. Existing HH updated with new scalar data right after coming into HOPE.
2. INDs assigned to incoming HH are not saved (`save_member` not called).

**POST rdi/<rdi>/push/ (PushToRDIView)**

```mermaid
flowchart TD
    P(["Assumption: RDI already exists in HOPE"]) -.- A
    A["POST rdi/&lt;rdi&gt;/push/"] --> C["self.save_households(self.selected_rdi, ...)<br/>= HouseholdUploadMixin.save_households() (same function)"]
    subgraph LOOP["for each incoming HH"]
        D["build PendingHH (in memory)"] --> E["_manage_collision"]
        E --> F{collides?}
        F -->|N| G["hh.save() + save_member()"]
        F -->|Y| H["continue<br/>hh.save() and save_member() skipped"]
    end
    C --> D
```

Result:
1. Existing HH updated with new data right after coming into HOPE.
2. INDs assigned to incoming HH are not saved (`save_member` not called).

Example — member skipped (same for `rdi/upload/`)

Assumptions:

- The program has collision detection ENABLED.
- Population (merged): household with key `HH-1`, one member Bob with key `IND-B`.
- The push sends a household with the same key `HH-1`, so it collides.

| | HH-1 members |
|---|---|
| Population | Bob (`IND-B`) |
| Push | Bob (`IND-B`), Anna (`IND-A`, new) |
| Result | Bob (`IND-B`), HH-1 fields updated |

Anna never reaches HOPE.

**POST rdi/<rdi>/push/lax/households/ (CreateLaxHouseholds)**

```mermaid
flowchart TD
    P(["Assumptions: RDI already exists in HOPE<br/>Pending INDs already exist in HOPE (no HH)"]) -.- A
    A["POST rdi/&lt;rdi&gt;/push/lax/households/"] --> C["_validate_and_collect_payloads()"]
    subgraph LOOP["for each incoming HH"]
        D["build PendingHH (in memory)"] --> E["_manage_collision"]
        E --> F{collides?}
        F -->|N| G["HH saved, INDs linked to it"]
        F -->|Y| H["continue<br/>HH never saved, INDs stay with no HH"]
    end
    C --> D
```

Result:
1. Existing HH updated with new data right after coming into HOPE.
2. New HH is removed.
3. INDs got abandoned and can be merged without HH assigned

Example — pending INDs orphaned

Assumptions:

- The program has collision detection ENABLED.
- Population (merged): household with key `HH-1`, one member Bob with key `IND-B`.
- The push sends a household with the same key `HH-1`, so it collides.
- Bob (`IND-B`) and Anna (`IND-A`) were already pushed as pending individuals in this RDI.

| | HH-1 members | No household |
|---|---|---|
| Population | Bob (`IND-B`) | |
| Push | Bob (`IND-B`), Anna (`IND-A`) | |
| Result | Bob (`IND-B`), HH-1 fields updated | Bob (`IND-B`), Anna (`IND-A`) |

After the RDI merge, Bob is in the population twice and both new records have no household.

## Other Ingestion paths (e.g. XLSX)

These paths never call `_manage_collision`. They store everything as pending and handle collisions at merge time in `RdiMergeTask.execute` (`src/hope/apps/registration_data/tasks/rdi_merge.py:165`).

```mermaid
flowchart TD
    A["Import: HHs and INDs stored as PENDING"] --> C
    subgraph MERGE["RDI merge (one DB transaction)"]
        C["0\. Process collisions<br/>incoming HH copied onto existing HH,<br/>incoming copy removed"] --> D["1\. Change statuses to MERGED<br/>(collided HHs and their INDs excluded)"]
        D --> E["2\. Add INDs to ES index"]
        E --> F["3\. Biographic dedup against population (ES)<br/>sets duplicate status per IND"]
        F --> G["4\. Sanction list check + document dedup"]
        G --> I["5\. Biometric dedup tickets (HDE pairs)"]
        I --> J["6\. RDI status MERGED +<br/>update RDI duplicate statistics"]
    end
```


## Open questions

1. https://github.com/unicef/hope/pull/6525#discussion_r4561585374
    ```
    Does CW has a way to specify identification_key when pushing individuals? Or will it always be None here? @ntrncic
    ```
    TODO: Add more context to that
