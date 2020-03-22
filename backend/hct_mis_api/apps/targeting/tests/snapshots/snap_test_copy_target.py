# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestTargetPopulationQuery::test_copy_target 1'] = {
    'data': {
        'copyTarget': {
            'targetPopulation': {
                'createdAt': '2020-03-22T20:57:28.070876',
                'createdBy': {
                    'firstName': 'Austin',
                    'id': 'VXNlck5vZGU6ZWU3NTI2MmEtMTIwZS00MGEzLTgzZjUtNjA2ODdiYzQ4OTkx',
                    'lastName': 'Hunter'
                },
                'id': 'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6NTdhZWI0OGYtMjNjZi00MjliLTgxMDItNTc0NWIxMmI0OWU5',
                'lastEditedAt': '2020-03-22T20:57:28.070915',
                'name': 'Test New Copy Name',
                'status': 'FINALIZED',
                'targetRules': {
                    'totalCount': 0
                },
                'totalFamilySize': None,
                'totalHouseholds': 0
            }
        }
    }
}
