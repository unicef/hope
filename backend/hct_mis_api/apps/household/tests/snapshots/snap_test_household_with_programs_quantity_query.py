# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestHouseholdWithProgramsQuantityQuery::test_household_query_single_with_programs_quantity_0_with_permission 1'] = {
    'data': {
        'household': {
            'programsWithDeliveredQuantity': [
                {
                    'name': 'Test program ONE',
                    'quantity': [
                        {
                            'currency': 'USD',
                            'totalDeliveredQuantity': '483.00'
                        },
                        {
                            'currency': 'AFG',
                            'totalDeliveredQuantity': '1033.00'
                        }
                    ]
                },
                {
                    'name': 'Test program TWO',
                    'quantity': [
                        {
                            'currency': 'USD',
                            'totalDeliveredQuantity': '1022.00'
                        }
                    ]
                },
                {
                    'name': 'Test program THREE',
                    'quantity': [
                        {
                            'currency': 'USD',
                            'totalDeliveredQuantity': '166.00'
                        },
                        {
                            'currency': 'PLN',
                            'totalDeliveredQuantity': '666.00'
                        }
                    ]
                }
            ]
        }
    }
}

snapshots['TestHouseholdWithProgramsQuantityQuery::test_household_query_single_with_programs_quantity_1_without_permission 1'] = {
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
