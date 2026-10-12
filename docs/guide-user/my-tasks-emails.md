---
title: My Tasks Emails
tags:
    - Grievance
    - Notifications
    - My Tasks
---

# My Tasks Emails

HOPE emails you when a tab of your [My Tasks](my-tasks.md) page changed since you last opened that
tab, and reminds you if you then stay away. Nothing is emailed about a ticket you have already seen
there, and nothing you did yourself ever triggers an email.

---

## What counts as a change

A ticket counts as changed for you when somebody else, after you last opened the tab it shows up on:

| Did this | It shows up on |
|---|---|
| created a ticket that nobody is assigned to, in a programme you may assign in | Needs assignment |
| assigned a ticket to you | Assigned to you |
| edited, moved to another status or added a note to a ticket assigned to you | Assigned to you |
| sent a ticket for approval that you may approve | Pending approval |

Closed tickets never count, and neither does anything you did yourself: assigning a ticket to
yourself, editing or closing your own ticket, or sending it for approval.

---

## The email

One email per business area, with the business area in the subject:

> **[Somalia] HOPE: you have new tasks**
>
> Tickets on your My Tasks page were created or changed since you last opened it. (Somalia)
>
> Assigned to you — *open My Tasks*
>
> Pending approval — *open My Tasks*

It names the tabs that changed, each with a link that opens My Tasks on that tab. It carries no
counts and no ticket IDs.

---

## When it is sent

The check runs every `MY_TASKS_MONITOR_WINDOW` days (one by default, so every day) at **06:00** in
your own timezone (`GRIEVANCE_NOTIFICATION_HOUR`). A user with no timezone set is treated as being
in the business area's timezone.

1. The first check after something changed, you get one email.
2. After that, nothing more is sent until you open My Tasks, however many further changes arrive.
3. If you have not opened My Tasks `MY_TASKS_ALARM_WINDOW` days after that email (seven by
   default), you get a reminder.
4. The reminder repeats every `MY_TASKS_REPEAT_EACH` days (two by default) for as long as the
   changes are still waiting.

Opening any tab of My Tasks ends the cycle. Each tab counts its changes from the last time you
opened that tab, so a tab you did not open keeps its changes, and the next morning's email names it
again.

Tracking starts for each user and business area the first time they open My Tasks or the first
time the check looks at them. Changes from before that point are never emailed.

---

## Turning it on

Three switches, all of which must be on:

| Where | Setting |
|---|---|
| Global (Constance) | `ENABLE_MAILJET` — sending email at all |
| Global (Constance) | `SEND_GRIEVANCES_NOTIFICATION` — grievance emails specifically |
| Per business area | **Enable email notification** |

The three windows are Constance settings too: `MY_TASKS_MONITOR_WINDOW`, `MY_TASKS_ALARM_WINDOW`
and `MY_TASKS_REPEAT_EACH`, all in days.

---

## Overdue thresholds

A ticket counts as overdue once it is older than the threshold for its category:

| Setting | Default | Applies to |
|---|---|---|
| `GRIEVANCE_OVERDUE_THRESHOLD_SENSITIVE` | 1 day | Sensitive Grievance tickets |
| `GRIEVANCE_OVERDUE_THRESHOLD_NON_SENSITIVE` | 30 days | every other category |

Both are measured from the ticket's creation date and drive the **Overdue Only** filter on My
Tasks. Being overdue does not by itself trigger an email.
