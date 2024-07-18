# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDataCollectionTypeSchema::test_dct_with_unknown_code_is_not_in_list 1'] = {
    'data': {
        'dataCollectionTypeChoices': [
            {
                'name': 'Size Only',
                'value': 'size_only'
            },
            {
                'name': 'Partial',
                'value': 'partial'
            },
            {
                'name': 'Full',
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
                'displayName': 'Yes/No',
                'value': 'BOOLEAN'
            }
        ]
    }
}
