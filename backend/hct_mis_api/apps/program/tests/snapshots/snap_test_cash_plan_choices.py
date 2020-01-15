# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCashPlanChoices::test_status_choices_query 1'] = {
    'data': {
        'cashPlanStatusChoices': [
            [
                'NOT_STARTED',
                'NOT_STARTED'
            ],
            [
                'STARTED',
                'STARTED'
            ],
            [
                'COMPLETE',
                'COMPLETE'
            ]
        ]
    }
}
