# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestPaymentPlanQueries::test_fetch_payment_plan_status_choices 1'] = {
    'data': {
        'paymentPlanStatusChoices': [
            {
                'name': 'Accepted',
                'value': 'ACCEPTED'
            },
            {
                'name': 'Draft',
                'value': 'DRAFT'
            },
            {
                'name': 'Finished',
                'value': 'FINISHED'
            },
            {
                'name': 'In Approval',
                'value': 'IN_APPROVAL'
            },
            {
                'name': 'In Authorization',
                'value': 'IN_AUTHORIZATION'
            },
            {
                'name': 'In Review',
                'value': 'IN_REVIEW'
            },
            {
                'name': 'Locked',
                'value': 'LOCKED'
            },
            {
                'name': 'Locked FSP',
                'value': 'LOCKED_FSP'
            },
            {
                'name': 'Open',
                'value': 'OPEN'
            },
            {
                'name': 'Preparing',
                'value': 'PREPARING'
            }
        ]
    }
}
