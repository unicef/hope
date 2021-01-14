# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestProgramChoices::test_program_frequency_of_payments_choices 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "programFrequencyOfPaymentsChoices" on type "Query".'
        }
    ]
}

snapshots['TestProgramChoices::test_program_scope_choices 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "programScopeChoices" on type "Query". Did you mean "roleChoices"?'
        }
    ]
}

snapshots['TestProgramChoices::test_program_sector_choices 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "programSectorChoices" on type "Query". Did you mean "reportStatusChoices", "maritalStatusChoices", "roleChoices" or "userStatusChoices"?'
        }
    ]
}

snapshots['TestProgramChoices::test_status_choices_query 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "programStatusChoices" on type "Query". Did you mean "reportStatusChoices", "maritalStatusChoices", "userStatusChoices", "residenceStatusChoices" or "countriesChoices"?'
        }
    ]
}
