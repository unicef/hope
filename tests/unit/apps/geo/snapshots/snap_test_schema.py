# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestSchema::test_get_areas_tree 1'] = {
    'data': {
        'allAreasTree': [
            {
                'areas': [
                    {
                        'areas': [
                            {
                                'areas': [
                                ],
                                'level': 3,
                                'name': 'City3',
                                'pCode': 'UA112233'
                            }
                        ],
                        'level': 2,
                        'name': 'City2',
                        'pCode': 'UA1122'
                    }
                ],
                'level': 1,
                'name': 'City1',
                'pCode': 'UA11'
            }
        ]
    }
}
