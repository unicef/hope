# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestHouseholdUpdate::test_household_update_authenticated 1'] = {
    'data': {
        'updateHousehold': {
            'household': {
                'address': 'this is my address',
                'familySize': 6,
                'householdCaId': '2b7f0db7-9010-4d1d-8b1f-19357b29c7b0',
                'nationality': 'AD',
                'residenceStatus': 'REFUGEE'
            }
        }
    }
}

snapshots['TestHouseholdUpdate::test_household_update_not_authenticated 1'] = {
    'data': {
        'updateHousehold': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User is not authenticated.',
            'path': [
                'updateHousehold'
            ]
        }
    ]
}
