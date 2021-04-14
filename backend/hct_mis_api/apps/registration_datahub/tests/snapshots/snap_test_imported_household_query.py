# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestImportedHouseholdQuery::test_imported_household_query_all_0_with_permission 1'] = {
    'data': {
        'allImportedHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 1
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 5
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 11
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 14
                    }
                }
            ]
        }
    }
}

snapshots['TestImportedHouseholdQuery::test_imported_household_query_all_1_without_permission 1'] = {
    'data': {
        'allImportedHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allImportedHouseholds'
            ]
        }
    ]
}

snapshots['TestImportedHouseholdQuery::test_imported_household_query_single_0_with_permission 1'] = {
    'data': {
        'importedHousehold': {
            'address': 'Lorem Ipsum',
            'countryOrigin': 'Poland',
            'size': 2
        }
    }
}

snapshots['TestImportedHouseholdQuery::test_imported_household_query_single_1_without_permission 1'] = {
    'data': {
        'importedHousehold': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'importedHousehold'
            ]
        }
    ]
}
