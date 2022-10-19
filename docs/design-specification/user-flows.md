# User Flows

## Summary

To view the latest flow diagrams for the HCT-MIS system, please view the following [**Link**](https://www.lucidchart.com/invitations/accept/cddd9508-7562-4cd5-adc5-f16a0d695752).

## Registration / Start the Flow:

```mermaid
%%{init: { "theme": "dark" } }%%
graph LR
    A[Calculate on options<br/>without data]
    --> B[Create intervention]
    --> C[Set up registration form]
    --> D[Import Beneficiary lists<br/>from other sources]
    --> E[Register beneficiaries,<br/>in the field]
    --> F[Check for duplicates,<br/>remove duplicated data]
```

## Targeting

```mermaid
%%{init: { "theme": "dark" } }%%
graph LR
    A[Filter/Calculate households that can<br/>be enrolled to the Intervention along<br/>with basic entitlement calculation]
    --> B["Create Draft Cash Plan<br/>(outside of Intervention, no<br/> approval process needed)"]
```

## Intervention Management

```mermaid
%%{init: { "theme": "dark" } }%%
graph TB
    A[Create Intervention]
    --> B[Assign Flexible attributes<br/>to Intervention if any]
    --> C[Assign FSPs to<br/>Intervention]
    --> D["Create a (first) Cycle<br/>(each cycle in Intervention<br/> is created manually)"]
    --> E["Associate draft cash plan<br/>with the cycle. This will<br/>split the draft cash plan<br/>households into multiple<br/>#quot;payment lists#quot; grouped by FSPs"]
    --> F[Approval / review process<br/>for each payment list.<br/>Overall approval then of<br/>the cycle by senior level]
    --> G["Send payment lists to<br/>financial gateway. Eg<br/>$700k transaction from<br/>UNICEF bank to FSP. FSP<br/>sends back transaction details"]
    --> H["Reconcillation of data.<br/>Two of them per previous<br/>step. Potentially get<br/>refund from FSP to<br/>UNICEF bank account"]
```

## Payment Verification

```mermaid
%%{init: { "theme": "dark" } }%%
graph LR
    A["View the list of transactions with<br/>statuses (flags) filtering"]
    --> B["Check the data from Financial Provider<br/>about each transaction - status, date,<br/>amount"]
    --> C["Contact with Beneficiary to verify<br/>payment on their end. Could be<br/>automated or via 3<sup>rd</sup> party monitor"]
    --> D["Set appropriate flag for Beneficiary<br/>status of payment or lack of<br/>verification (were not able to make<br/>contact with them)"]
    --> E["Incase of any problems, create ticket<br/>for Grievance team"]
    F["Go to Cycle and generate payment<br/>verification lists per FSP. Flagging this<br/>transaction as #quot;due for verification#quot;"] --> C
```

- does the data from Financial Provider occur automatically or unicef user needs to click eg. "sync" buton
- who decides what status / flag it is - unicef user / Provider?

## Grievance / Feedback

```mermaid
%%{init: { "theme": "dark" } }%%
graph LR
    A["Receive users opinion<br/>from many sources - <br/>face2face, phone calls,<br/> sms, tickets from Payment<br/> Verification team etc"]
    --> B["Verify Beneficiary identity<br/> before collecting the<br/> grievance / feedback"]
    --> C["Create ticket in the system<br/> with full description of the <br/>problem, if not created by<br/> Payment Verification team"]
    --> D["Follow up on ticket to <br/>close it finally"]
```

## Grievance / Change of Personal Information

```mermaid
%%{init: { "theme": "dark" } }%%
graph LR
    A["Beneficiary contacts <br/>call center"]
    --> B["Beneficiary is being<br/> verified"]
    --> C["Types of greviance #gt;<br/> Change of Personal<br/> Information"]
    --> D["Types of Personal<br/>Information #gt; Surname"]
    --> E["Change from A to B"]
    --> F["Create ticket<br/> (logs are being gathered)"]
    --> G["Assign ticket to Program<br/> Manager"]
    --> H["Program Manager reviews<br/> changes and approves<br/> them"]
```

## Flexible Fields

```mermaid
%%{init: { "theme": "dark" } }%%
graph LR
    AA(Creating an<br/>intervention) --> AB
    subgraph A
    AB["Tap #quot;Add<br/> Intervention#quot; Button"]
    --> AC["Name Intervention to<br/> save it as a draft"]
    --> AD["Registration settings: <br/>Pick one or more <br/>flexible fields"]
    --> AE["Mark some fields as required or not<br/> (maybe this hapens in flex field side<br/> not sure, drag them to decide on<br/> ordering etc.)"]
    end

    BA("Creating a flexible<br/> field") --> BB
    subgraph B
    BB["Tap #quot;Add flex field#quot;<br/> Button"]
    --> BC["Name it, select type,<br/> other config options<br/> for it"]
    --> BD["Maybe choose to apply it<br/> to intervention (I'd leave it<br/> in intervention interface<br/> thought)"]
    --> BE["Maybe we need to say"]
    end

    classDef step fill:#009cc3,color:#fff;
    class AA,BA step
```
