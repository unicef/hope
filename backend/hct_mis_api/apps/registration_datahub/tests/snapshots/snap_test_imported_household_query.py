# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestImportedHouseholdQuery::test_imported_household_query_all 1'] = {
    'data': {
        'allImportedHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 2
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 5
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 1
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 11
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 14
                    }
                }
            ]
        }
    }
}

snapshots['TestImportedHouseholdQuery::test_imported_household_query_single 1'] = {
    'data': {
        'importedHousehold': {
            'address': 'Lorem Ipsum',
            'countryOrigin': 'PL',
            'size': 2
        }
    }
}
