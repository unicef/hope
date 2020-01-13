# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestProgramStatusChoices::test_status_choices_query 1'] = {
    'data': {
        'programStatusChoices': [
            [
                'DRAFT',
                'Draft'
            ],
            [
                'ACTIVE',
                'Active'
            ],
            [
                'FINISHED',
                'Finished'
            ]
        ]
    }
}
