# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestHouseholdWithProgramsQuantityQuery::test_household_query_single_0_with_permission 1'] = {
    'data': {
        'household': {
            'programsWithDeliveredQuantity': [
                {
                    'name': 'Test program ONE',
                    'quantity': [
                        {
                            'currency': 'USD',
                            'totalDeliveredQuantity': '450.00'
                        },
                        {
                            'currency': 'AFG',
                            'totalDeliveredQuantity': '900.00',
                        },
                    ]
                },
                {
                    'name': 'Test program TWO',
                    'quantity': [
                        {
                            'currency': 'USD',
                            'totalDeliveredQuantity': '900.00',
                        },
                    ]

                }
            ]
        }
    }
}

snapshots['TestHouseholdWithProgramsQuantityQuery::test_household_query_single_1_without_permission 1'] = {
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
