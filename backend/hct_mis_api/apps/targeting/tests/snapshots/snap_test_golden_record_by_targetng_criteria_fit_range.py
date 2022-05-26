# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GoldenRecordTargetingCriteriaFitRangeQueryTestCase::test_filter_records_by_fit_range_0 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'totalCount': 1
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaFitRangeQueryTestCase::test_filter_records_by_fit_range_1 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'totalCount': 1
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaFitRangeQueryTestCase::test_filter_records_by_fit_range_2 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'totalCount': 1
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaFitRangeQueryTestCase::test_filter_records_by_fit_range_3 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'totalCount': 3
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaFitRangeQueryTestCase::test_filter_records_by_fit_range_4 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'totalCount': 2
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaFitRangeQueryTestCase::test_filter_records_raises_error_when_min_is_higher_than_max 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 8
                }
            ],
            'message': 'Minimum number cannot be higher than maximum number.',
            'path': [
                'goldenRecordByTargetingCriteria'
            ]
        }
    ]
}
