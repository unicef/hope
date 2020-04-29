# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GoldenRecordTargetingCriteriaQueryTestCase::test_golden_record_by_targeting_criteria_size 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 7
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['GoldenRecordTargetingCriteriaQueryTestCase::test_golden_record_by_targeting_criteria_residence_status 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 7
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}
