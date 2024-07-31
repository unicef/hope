# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAllPduFields::test_pdu_subtype_choices_data 1'] = {
    'data': {
        'allPduFields': [
            {
                'labelEn': 'PDU Field 1',
                'name': 'pdu_field_1',
                'pduData': {
                    'numberOfRounds': 3,
                    'roundsNames': [
                        'Round 1',
                        'Round 2',
                        'Round 3'
                    ],
                    'subtype': 'DECIMAL'
                },
                'type': 'PDU'
            },
            {
                'labelEn': 'PDU Field 2',
                'name': 'pdu_field_2',
                'pduData': {
                    'numberOfRounds': 2,
                    'roundsNames': [
                        'Round 1',
                        'Round 2'
                    ],
                    'subtype': 'STRING'
                },
                'type': 'PDU'
            }
        ]
    }
}
