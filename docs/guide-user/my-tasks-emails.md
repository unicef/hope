---
title: My Tasks Emails
tags:
    - Grievance
    - Notifications
    - My Tasks
---

# My Tasks Emails

HOPE emails you when your [My Tasks](my-tasks.md) page holds a ticket you have not opened since
somebody else created or changed it, and reminds you while it stays unopened. Nothing is emailed
about a ticket you have already opened, and nothing you did yourself ever triggers an email.

---

## What counts as unread

A ticket is unread for you when somebody else, after you last opened that ticket:

| Did this | It shows up on |
|---|---|
| created a ticket that nobody is assigned to, in a programme you may assign in | Needs assignment |
| assigned a ticket to you | Assigned to you |
| edited, moved to another status or added a note to a ticket assigned to you | Assigned to you |
| sent a ticket for approval that you may approve | Pending approval |

Closed tickets never count, and neither does anything you did yourself: assigning a ticket to
yourself, editing or closing your own ticket, or sending it for approval. A ticket you have never
opened counts from the moment HOPE started tracking you in the business area (your first visit to
My Tasks, or the first check that looked at you), so nothing older than that is ever emailed.

---

## The email

One email per business area, with the business area in the subject:

> **[Somalia] HOPE: you have new tasks**
>
> Tickets on your My Tasks page were created or changed and you have not opened them yet.
>
> Assigned to you - *open My Tasks*
>
> Pending approval - *open My Tasks*

It names the tabs holding unread tickets, each with a link that opens My Tasks on that tab. It
carries no counts and no ticket IDs. The reminders are the same email with the subject
**[Somalia] HOPE reminder: you have new tasks** and "Reminder:" in front of the first sentence.

---

## When it is sent

The check runs every `MY_TASKS_MONITOR_WINDOW` days (one by default, so every day) at **06:00** in
your own timezone (`GRIEVANCE_NOTIFICATION_HOUR`). A user with no timezone set is treated as being
in the business area's timezone.

1. The first check that finds an unread ticket, you get one email.
2. After that, nothing more is sent however many further changes arrive.
3. If something is still unread `MY_TASKS_ALARM_WINDOW` days after that email (seven by default),
   you get a reminder.
4. The reminder repeats every `MY_TASKS_REPEAT_EACH` days (two by default) for as long as
   something stays unread.

The cycle ends once nothing is unread any more: you opened the last unread ticket, used **Mark all
as read** on the last tab with unread tickets, or a check found nothing unread. The next unread
ticket starts again with a "you have new tasks" email. Opening other tickets while one stays unread
does not restart the cycle, so the reminders keep their schedule.

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
