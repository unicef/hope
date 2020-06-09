# CashAssist glossary

Following are glossary terms that are CashAssist specific. These should help in mapping of terms and also as we integrate with CashAssist to fully understand their concepts for a smoother integration.

For an overview of CashAssist you may look at this slide deck: [https://drive.google.com/file/d/1tRdR9nNgfJ3ni818o3DY0Ha6LnETfd5t/view](https://drive.google.com/file/d/1tRdR9nNgfJ3ni818o3DY0Ha6LnETfd5t/view)

<table>
  <thead>
    <tr>
      <th style="text-align:left">Term / Acronym</th>
      <th style="text-align:left">Definition / Detail</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:left">Access Management Portal</td>
      <td style="text-align:left">New user management system being put in place by UNHCR.
        <br />
        <br />Split between someone who can request and someone who can approve. Delegating
        down to BU&apos;s. Someone in their operation would approve. This model
        can be extended to UNICEF as well then. First phase goes live in December,</td>
    </tr>
    <tr>
      <td style="text-align:left">Assistance Measurement</td>
      <td style="text-align:left">It is the currency for entitlement</td>
    </tr>
    <tr>
      <td style="text-align:left">Assistance Package</td>
      <td style="text-align:left">
        <p>Target population + distribution modalities. One cash plan can have many
          assistance packages.</p>
        <p></p>
        <p>A hierarchical model (see fig. 1) that pairs target list with distribution
          modality (which is explained below)</p>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">Assistance through</td>
      <td style="text-align:left">The name of the financial service provider</td>
    </tr>
    <tr>
      <td style="text-align:left">Assistance type</td>
      <td style="text-align:left">How we&apos;re going to pay.</td>
    </tr>
    <tr>
      <td style="text-align:left">BU</td>
      <td style="text-align:left">&apos;Business Unit&apos;, which will be named &quot;UNICEF Jordan&quot;,
        &quot;UNICEF Somalia&quot;, etc. and programs/users/beneficiary data are
        associated with this BU on CashAssist side. In the UNICEF terminology this
        somewhat maps to the &apos;Business Area&apos;.</td>
    </tr>
    <tr>
      <td style="text-align:left">Card Size</td>
      <td style="text-align:left">The number of people covered</td>
    </tr>
    <tr>
      <td style="text-align:left">Cash Plan</td>
      <td style="text-align:left">Grouping of assistance packages for a program. Mixed delivery types in
        the same cash plan are not allowed, so a program can have multiple cash
        plans for instance when delivering voucher and cash-in-hand.</td>
    </tr>
    <tr>
      <td style="text-align:left">Conditional Values</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Corticon</td>
      <td style="text-align:left">
        <p>Also called &quot;rule engine&quot;.
          <br />
        </p>
        <p>Mainly used to target households and calculate entitlements. Pushes data
          (ben. id + entitlement etc.) to CashAssist then.</p>
        <p></p>
        <p>In the UNHCR azure cloud.</p>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">Delivery Type</td>
      <td style="text-align:left">Deposit to card, transfer or cash</td>
    </tr>
    <tr>
      <td style="text-align:left">Distribution Modality</td>
      <td style="text-align:left">Grouping of assistance measurement (currency), delivery type, entitlement
        formula and FSP</td>
    </tr>
    <tr>
      <td style="text-align:left">Distribution Level</td>
      <td style="text-align:left">Registration Groups (households) or Individuals</td>
    </tr>
    <tr>
      <td style="text-align:left">DM</td>
      <td style="text-align:left">Distribution Modality - Acronym in Rule Engine.</td>
    </tr>
    <tr>
      <td style="text-align:left">Eligible</td>
      <td style="text-align:left">Person who is associated with a program (not targeted to it).</td>
    </tr>
    <tr>
      <td style="text-align:left">Entitlement Formula</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Global Distribution Tool (GDT)</td>
      <td style="text-align:left">
        <p>Loads down payment records to a local environment and go to village on
          a truck for example. Have downloaded biometric data. Will pull payment
          record. Offline tool on a laptop and biometrics.</p>
        <p>
          <br />Also used to distributing cards.
          <br />
        </p>
        <p>Can be used for non-food items as well. Its linked to Progres v4.</p>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">Golden Record</td>
      <td style="text-align:left">Core fields required for household and beneficiary.</td>
    </tr>
    <tr>
      <td style="text-align:left">Hard Block</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Household data</td>
      <td style="text-align:left">Doesn&apos;t have individual level data. Just primary + 2 adults/3 kids.</td>
    </tr>
    <tr>
      <td style="text-align:left">Import View</td>
      <td style="text-align:left">To import data based on some filtered list/data.</td>
    </tr>
    <tr>
      <td style="text-align:left">Master Cash Plan</td>
      <td style="text-align:left">Allows to bundle several cash plans into one, in those instances in which
        we want to send the payment instructions of multiple cash plans all at
        the same time to the FSPs</td>
    </tr>
    <tr>
      <td style="text-align:left">No-pay lists</td>
      <td style="text-align:left">Blacklisted registration groups or individuals</td>
    </tr>
    <tr>
      <td style="text-align:left">NPO</td>
      <td style="text-align:left">Kind of a confirmation that payment has been sent. Fetches data from the
        ERP. UNICEF doesn&apos;t have an NPO. Its at the cash plan level.</td>
    </tr>
    <tr>
      <td style="text-align:left">Program</td>
      <td style="text-align:left">Same as intervention. States are active, inactive, erroneous, under preparation.</td>
    </tr>
    <tr>
      <td style="text-align:left">Progres</td>
      <td style="text-align:left">v4 - beneficiary management system (registration system sort of). Its
        built on MSFT Dynamics.</td>
    </tr>
    <tr>
      <td style="text-align:left">PMT -</td>
      <td style="text-align:left">Acronym in Rule Engine for &quot;Payment&quot; - A generic Payment Service
        in Rule Server.</td>
    </tr>
    <tr>
      <td style="text-align:left">Reception Group</td>
      <td style="text-align:left">Comes from v3 Progres. Something like a reception record. Eg. refugee
        coming in on their own. Would not be needed as a concept in HCT MIS.</td>
    </tr>
    <tr>
      <td style="text-align:left">Registration group</td>
      <td style="text-align:left">Groups of associated individuals. Can assign multiple entitlement cards...</td>
    </tr>
    <tr>
      <td style="text-align:left">Rule Engine</td>
      <td style="text-align:left">Used interchangeable with Corticon.</td>
    </tr>
    <tr>
      <td style="text-align:left">Scope</td>
      <td style="text-align:left">Drives validation of the program through its lifecycle. Eg. &quot;scope
        of the program&quot;.</td>
    </tr>
    <tr>
      <td style="text-align:left">Soft Block</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Staging area</td>
      <td style="text-align:left">On-prem currently. MS SQL server. Push of data to it is not allowed.</td>
    </tr>
    <tr>
      <td style="text-align:left">Target Population/List</td>
      <td style="text-align:left">List of either registration group, individuals or households.</td>
    </tr>
  </tbody>
</table>



