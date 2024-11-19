# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestProgramChoices::test_program_cycle_status_choices 1'] = {
    'data': {
        'programCycleStatusChoices': [
            {
                'name': 'Active',
                'value': 'ACTIVE'
            },
            {
                'name': 'Draft',
                'value': 'DRAFT'
            },
            {
                'name': 'Finished',
                'value': 'FINISHED'
            }
        ]
    }
}

snapshots['TestProgramChoices::test_program_frequency_of_payments_choices 1'] = {
    'data': {
        'programFrequencyOfPaymentsChoices': [
            {
                'name': 'One-off',
                'value': 'ONE_OFF'
            },
            {
                'name': 'Regular',
                'value': 'REGULAR'
            }
        ]
    }
}

snapshots['TestProgramChoices::test_program_scope_choices 1'] = {
    'data': {
        'programScopeChoices': [
            {
                'name': 'For partners',
                'value': 'FOR_PARTNERS'
            },
            {
                'name': 'Unicef',
                'value': 'UNICEF'
            }
        ]
    }
}

snapshots['TestProgramChoices::test_program_sector_choices 1'] = {
    'data': {
        'programSectorChoices': [
            {
                'name': 'Child Protection',
                'value': 'CHILD_PROTECTION'
            },
            {
                'name': 'Education',
                'value': 'EDUCATION'
            },
            {
                'name': 'Health',
                'value': 'HEALTH'
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
                'name': 'Active',
                'value': 'ACTIVE'
            },
            {
                'name': 'Draft',
                'value': 'DRAFT'
            },
            {
                'name': 'Finished',
                'value': 'FINISHED'
            }
        ]
    }
}
