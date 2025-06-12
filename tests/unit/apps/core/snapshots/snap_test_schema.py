# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestAllCollectorsFields::test_collectors_fields_choices_data 1'] = {
    'data': {
        'allCollectorFieldsAttributes': [
            {
                'labelEn': 'Bank Number',
                'name': 'bank__number'
            },
            {
                'labelEn': 'Mobile Number',
                'name': 'mobile__number'
            }
        ]
    }
}

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

snapshots['TestDataCollectionTypeSchema::test_dct_with_unknown_code_is_not_in_list 1'] = {
    'data': {
        'dataCollectionTypeChoices': [
            {
                'name': 'Size Only',
                'type': 'STANDARD',
                'value': 'size_only'
            },
            {
                'name': 'Partial',
                'type': 'SOCIAL',
                'value': 'partial'
            },
            {
                'name': 'Full',
                'type': 'STANDARD',
                'value': 'full'
            }
        ]
    }
}

snapshots['TestPDUSubtypeChoices::test_pdu_subtype_choices_data 1'] = {
    'data': {
        'pduSubtypeChoices': [
            {
                'displayName': 'Date',
                'value': 'DATE'
            },
            {
                'displayName': 'Number',
                'value': 'DECIMAL'
            },
            {
                'displayName': 'Text',
                'value': 'STRING'
            },
            {
                'displayName': 'Boolean (true/false)',
                'value': 'BOOL'
            }
        ]
    }
}
