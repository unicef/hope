# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestProgramQuery::test_single_program_query_0_with_permission 1'] = {
    'data': {
        'program': {
            'name': 'Test Program Query',
            'pduFields': [
                {
                    'name': 'PDU Field 1',
                    'pduData': {
                        'numberOfRounds': 3,
                        'roundsNames': [
                            'Round 1',
                            'Round 2',
                            'Round 3'
                        ],
                        'subtype': 'DECIMAL'
                    }
                },
                {
                    'name': 'PDU Field 2',
                    'pduData': {
                        'numberOfRounds': 2,
                        'roundsNames': [
                            'Round January',
                            'Round February'
                        ],
                        'subtype': 'STRING'
                    }
                },
                {
                    'name': 'PDU Field 3',
                    'pduData': {
                        'numberOfRounds': 1,
                        'roundsNames': [
                            'Round *'
                        ],
                        'subtype': 'DATE'
                    }
                },
                {
                    'name': 'PDU Field 4',
                    'pduData': {
                        'numberOfRounds': 2,
                        'roundsNames': [
                            'Round A',
                            'Round B'
                        ],
                        'subtype': 'BOOLEAN'
                    }
                }
            ],
            'status': 'ACTIVE'
        }
    }
}

snapshots['TestProgramQuery::test_single_program_query_1_without_permission 1'] = {
    'data': {
        'program': None
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
                'program'
            ]
        }
    ]
}
