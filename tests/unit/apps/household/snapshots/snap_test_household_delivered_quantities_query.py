# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestHouseholdDeliveredQuantitiesQuery::test_household_query_single_0_with_permission 1'] = {
    'data': {
        'household': {
            'deliveredQuantities': [
                {
                    'currency': 'USD',
                    'totalDeliveredQuantity': '83.00'
                },
                {
                    'currency': 'AFG',
                    'totalDeliveredQuantity': '233.00'
                }
            ]
        }
    }
}

snapshots['TestHouseholdDeliveredQuantitiesQuery::test_household_query_single_1_without_permission 1'] = {
    'data': {
        'household': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'household'
            ]
        }
    ]
}
