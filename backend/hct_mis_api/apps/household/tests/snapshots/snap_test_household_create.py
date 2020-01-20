# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestHouseholdCreate::test_household_consent_validation_no_file 1'] = {
    'data': {
        'createHousehold': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Consent image is required.',
            'path': [
                'createHousehold'
            ]
        }
    ]
}

snapshots['TestHouseholdCreate::test_household_consent_validation_not_image 1'] = {
    'data': {
        'createHousehold': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'File is not a valid image',
            'path': [
                'createHousehold'
            ]
        }
    ]
}

snapshots['TestHouseholdCreate::test_household_create_authenticated 1'] = {
    'data': {
        'createHousehold': {
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

snapshots['TestHouseholdCreate::test_household_create_not_authenticated 1'] = {
    'data': {
        'createHousehold': None
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
                'createHousehold'
            ]
        }
    ]
}
