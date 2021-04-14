# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase::test_golden_record_by_targeting_criteria_size 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'maritalStatus': 'MARRIED',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    }
}
