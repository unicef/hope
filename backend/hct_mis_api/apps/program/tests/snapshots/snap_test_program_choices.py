# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestProgramChoices::test_program_frequency_of_payments_choices 1'] = {
    'data': {
        'programFrequencyOfPaymentsChoices': [
            {
                'name': 'Regular',
                'value': 'REGULAR'
            },
            {
                'name': 'One-off',
                'value': 'ONE_OFF'
            }
        ]
    }
}

snapshots['TestProgramChoices::test_program_scope_choices 1'] = {
    'data': {
        'programScopeChoices': [
            {
                'name': 'Full',
                'value': 'FULL'
            },
            {
                'name': 'Partial',
                'value': 'PARTIAL'
            },
            {
                'name': 'No Integration',
                'value': 'NO_INTEGRATION'
            }
        ]
    }
}

snapshots['TestProgramChoices::test_program_sector_choices 1'] = {
    'data': {
        'programSectorChoices': [
            {
                'name': 'Child Protection',
                'value': 'CHILD PROTECTION'
            },
            {
                'name': 'Education',
                'value': 'EDUCATION'
            },
            {
                'name': 'Gender',
                'value': 'GENDER'
            },
            {
                'name': 'Health',
                'value': 'HEALTH'
            },
            {
                'name': 'HIV / AIDS',
                'value': 'HIV_AIDS'
            },
            {
                'name': 'Multi Purpose',
                'value': 'MULTI_PURPOSE'
            },
            {
                'name': 'Nutrition',
                'value': 'NUTRITION'
            },
            {
                'name': 'Social Policy',
                'value': 'SOCIAL_POLICY'
            },
            {
                'name': 'WASH',
                'value': 'WASH'
            }
        ]
    }
}

snapshots['TestProgramChoices::test_status_choices_query 1'] = {
    'data': {
        'programStatusChoices': [
            {
                'name': 'Draft',
                'value': 'DRAFT'
            },
            {
                'name': 'Active',
                'value': 'ACTIVE'
            },
            {
                'name': 'Finished',
                'value': 'FINISHED'
            }
        ]
    }
}
