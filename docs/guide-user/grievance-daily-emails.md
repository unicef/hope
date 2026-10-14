---
title: Grievance Daily Emails
tags:
    - Grievance
    - Notifications
    - My Tasks
---

# Grievance Daily Emails

HOPE used to email an operator on every event: a ticket created, a ticket assigned, a ticket
changed, and a reminder for each overdue ticket — one message per ticket, per event.

Those per-ticket emails are gone. In their place every recipient gets **at most four emails a day**,
each carrying a count and a link into [My Tasks](my-tasks.md) rather than a list of tickets.

---

## The four emails

| Email | Sent to | Counts |
|---|---|---|
| **Tickets Needing Assignment** | everyone who may assign tickets in the programme | every active ticket with no assignee |
| **Tickets Assigned to You** | the new assignee | tickets assigned to them that day |
| **Overdue Tickets** | the assignee | their tickets past the due date |
| **Updated Tickets** | the assignee and the creator | their tickets changed that day by someone else |

An email is only sent when its count is above zero.

### What the recipient sees

Each email gives a one-line introduction and then one line per category, with its own link:

> Grievance tickets assigned to you are past their due date.
>
> Sensitive: 2 tickets — *link*
>
> Other: 11 tickets — *link*

A line only appears when there is something to count, so an email may carry one category or both.

!!! note "No ticket is ever named in an email"
    The emails carry counts and links, never ticket IDs, subjects or beneficiary details. The
    ticket is only visible in HOPE, to someone who passed the permission check.

---

## What each email counts

**Tickets Needing Assignment** is scoped to the programmes each recipient may assign in. It is a
standing reminder rather than a report of the day: a ticket stays in the count until someone
assigns it.

**Tickets Assigned to You** counts any assignment made that day, a reassignment of an older ticket
included. Assigning a ticket to yourself does not mail you.

**Overdue Tickets** counts every overdue ticket assigned to the recipient, not only the ones due a
reminder. The email is only sent when at least one of those tickets is due a reminder:
once a ticket has been reported it is not reported again until its threshold has passed a second
time — thirty days for an ordinary ticket, one day for a sensitive one.

**Updated Tickets** counts tickets assigned to you, or created by you, that somebody else changed
that day. Your own edits never mail you, and a ticket assigned to you that same day is reported
once, as an assignment, not twice.

---

## Overdue thresholds

A ticket counts as overdue once it is older than the threshold for its category:

| Setting | Default | Applies to |
|---|---|---|
| `GRIEVANCE_OVERDUE_THRESHOLD_SENSITIVE` | 1 day | Sensitive Grievance tickets |
| `GRIEVANCE_OVERDUE_THRESHOLD_NON_SENSITIVE` | 30 days | every other category |

Both are measured from the ticket's creation date, and both are configurable per environment. The
same thresholds drive the **Overdue Only** filter on My Tasks, so the number in the email and the
list behind the link agree.

---

## When they are sent

The emails go out once a day at **06:00** in the recipient's own timezone, covering the previous
day. The hour is configurable with `GRIEVANCE_NOTIFICATION_HOUR`.

Recipients in different timezones are mailed in separate runs, each at 06:00 local time. A user
with no timezone set is treated as being in the business area's timezone.

Delivery is tracked for each email separately, so a run that fails before an email reaches the
mail queue re-sends only that one. A temporary failure at the mail provider is retried up to
three times by the mail queue itself.

---

## Turning them on

Three switches, all of which must be on:

| Where | Setting |
|---|---|
| Global (Constance) | `ENABLE_MAILJET` — sending email at all |
| Global (Constance) | `SEND_GRIEVANCES_NOTIFICATION` — grievance emails specifically |
| Per business area | **Enable email notification** |

---

## Following a link

Every link opens [My Tasks](my-tasks.md) with the tab and filters already applied — the sensitive
line of the overdue email opens **ASSIGNED TO ME** filtered to **Sensitive** and **Overdue Only**.
The filters are shown in the filter bar rather than applied invisibly, so the list can be widened
from there.
