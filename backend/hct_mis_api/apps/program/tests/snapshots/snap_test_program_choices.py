# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestProgramChoices::test_program_frequency_of_payments_choices 1'] = {
    'data': {
        'programFrequencyOfPaymentsChoices': [
            [
                'REGULAR',
                'Regular'
            ],
            [
                'ONE_OFF',
                'One-off'
            ]
        ]
    }
}

snapshots['TestProgramChoices::test_program_scope_choices 1'] = {
    'data': {
        'programScopeChoices': [
            [
                'FULL',
                'Full'
            ],
            [
                'PARTIAL',
                'Partial'
            ],
            [
                'NO_INTEGRATION',
                'No Integration'
            ]
        ]
    }
}

snapshots['TestProgramChoices::test_program_sector_choices 1'] = {
    'data': {
        'programSectorChoices': [
            [
                'CHILD',
                'Child'
            ],
            [
                'PROTECTION',
                'Protection'
            ],
            [
                'EDUCATION',
                'Education'
            ],
            [
                'GENDER',
                'Gender'
            ],
            [
                'HEALTH',
                'Health'
            ],
            [
                'HIV_AIDS',
                'HIV / AIDS'
            ],
            [
                'MULTI_PURPOSE',
                'Multi Purpose'
            ],
            [
                'NUTRITION',
                'Nutrition'
            ],
            [
                'SOCIAL_POLICY',
                'Social Policy'
            ],
            [
                'WASH',
                'WASH'
            ]
        ]
    }
}

snapshots['TestProgramChoices::test_status_choices_query 1'] = {
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
