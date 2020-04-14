# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GoldenRecordTargetingCriteriaQueryTestCase::test_golden_record_by_targeting_criteria_family_size 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'familySize': 2,
                        'residenceStatus': 'REFUGEE'
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
                        'familySize': 2,
                        'residenceStatus': 'REFUGEE'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}
