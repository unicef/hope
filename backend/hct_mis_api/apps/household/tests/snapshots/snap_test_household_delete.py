# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDeleteHousehold::test_delete_household_authenticated 1'] = {
    'data': {
        'deleteHousehold': {
            'ok': True
        }
    }
}

snapshots['TestDeleteHousehold::test_delete_household_not_authenticated 1'] = {
    'data': {
        'deleteHousehold': None
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
                'deleteHousehold'
            ]
        }
    ]
}
