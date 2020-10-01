# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestApproveTargetPopulationMutation::test_approve_fail_target_population 1'] = {
    'data': {
        'approveTargetPopulation': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 15,
                    'line': 3
                }
            ],
            'message': "['Only Target Population with status DRAFT can be approved']",
            'path': [
                'approveTargetPopulation'
            ]
        }
    ]
}

snapshots['TestApproveTargetPopulationMutation::test_approve_target_population 1'] = {
    'data': {
        'approveTargetPopulation': {
            'targetPopulation': {
                'households': {
                    'edges': [
                        {
                            'node': {
                                'residenceStatus': 'CITIZEN',
                                'size': 1
                            }
                        },
                        {
                            'node': {
                                'residenceStatus': 'CITIZEN',
                                'size': 2
                            }
                        }
                    ],
                    'totalCount': 2
                },
                'status': 'APPROVED'
            }
        }
    }
}
