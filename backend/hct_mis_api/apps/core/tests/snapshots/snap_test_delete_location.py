# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDeleteLocation::test_delete_location_authenticated 1'] = {
    'data': {
        'deleteLocation': {
            'ok': True
        }
    }
}

snapshots['TestDeleteLocation::test_delete_location_not_authenticated 1'] = {
    'data': {
        'deleteLocation': None
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
                'deleteLocation'
            ]
        }
    ]
}
