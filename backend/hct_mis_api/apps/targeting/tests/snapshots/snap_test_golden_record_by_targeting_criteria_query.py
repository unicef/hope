# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GoldenRecordTargetingCriteriaQueryTestCase::test_golden_record_by_targeting_criteria_size 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'REFUGEE',
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaQueryTestCase::test_golden_record_by_targeting_criteria_residence_status 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'REFUGEE',
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaQueryTestCase::test_golden_record_by_targeting_criteria_flex_field 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
            ],
            'totalCount': 0
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaQueryTestCase::test_golden_record_by_targeting_criteria_select_many 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
            ],
            'totalCount': 0
        }
    }
}
