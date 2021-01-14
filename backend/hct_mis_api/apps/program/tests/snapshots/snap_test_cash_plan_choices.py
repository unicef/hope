# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCashPlanChoices::test_status_choices_query 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "cashPlanStatusChoices" on type "Query". Did you mean "maritalStatusChoices", "userStatusChoices", "reportStatusChoices", "residenceStatusChoices" or "countriesChoices"?'
        }
    ]
}
