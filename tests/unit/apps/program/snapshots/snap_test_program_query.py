# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestProgramQuery::test_single_program_query_0_with_permission 1'] = {
    'data': {
        'program': {
            'canFinish': False,
            'name': 'Test Program Query',
            'pduFields': [
                {
                    'label': '{"English(EN)": "PDU Field 1"}',
                    'name': 'pdu_field_1',
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
                    'label': '{"English(EN)": "PDU Field 2"}',
                    'name': 'pdu_field_2',
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
                    'label': '{"English(EN)": "PDU Field 3"}',
                    'name': 'pdu_field_3',
                    'pduData': {
                        'numberOfRounds': 1,
                        'roundsNames': [
                            'Round *'
                        ],
                        'subtype': 'DATE'
                    }
                },
                {
                    'label': '{"English(EN)": "PDU Field 4"}',
                    'name': 'pdu_field_4',
                    'pduData': {
                        'numberOfRounds': 2,
                        'roundsNames': [
                            'Round A',
                            'Round B'
                        ],
                        'subtype': 'BOOL'
                    }
                }
            ],
            'status': 'ACTIVE',
            'targetPopulationsCount': 1
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
