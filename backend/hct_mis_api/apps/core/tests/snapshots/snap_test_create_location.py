# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateLocation::test_create_location_authenticated 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Cannot query field "name" on type "LocationNode".'
        },
        {
            'locations': [
                {
                    'column': 11,
                    'line': 6
                }
            ],
            'message': 'Cannot query field "country" on type "LocationNode".'
        }
    ]
}

snapshots['TestCreateLocation::test_create_location_not_authenticated 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Cannot query field "name" on type "LocationNode".'
        },
        {
            'locations': [
                {
                    'column': 11,
                    'line': 6
                }
            ],
            'message': 'Cannot query field "country" on type "LocationNode".'
        }
    ]
}
