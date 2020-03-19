# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestMetaDataFilterType::test_core_meta_type_query 1'] = {
    'data': {
        'allCoreFieldAttributes': [
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': 'number of years spent in school',
                'id': '05c6be72-22ac-401b-9d3f-0a7e7352aa87',
                'label': '{"English(EN)": "years in school"}',
                'name': 'years_in_school',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': 'age in years',
                'id': 'a1741e3c-0e24-4a60-8d2f-463943abaebb',
                'label': '{"English(EN)": "age"}',
                'name': 'age',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': 'how many persons in the household',
                'id': 'd6aa9669-ae82-4e3c-adfe-79b5d95d0754',
                'label': '{"English(EN)": "Family Size"}',
                'name': 'family_size',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'label': 'Refugee',
                        'name': 'REFUGEE'
                    },
                    {
                        'label': 'Migrant',
                        'name': 'MIGRANT'
                    },
                    {
                        'label': 'Citizen',
                        'name': 'CITIZEN'
                    },
                    {
                        'label': 'IDP',
                        'name': 'IDP'
                    },
                    {
                        'label': 'Other',
                        'name': 'OTHER'
                    }
                ],
                'hint': 'residential status of household',
                'id': '3c2473d6-1e81-4025-86c7-e8036dd92f4b',
                'label': '{"English(EN)": "Residence Status"}',
                'name': 'residence_status',
                'required': True,
                'type': 'SELECT_ONE'
            }
        ],
        'allFlexFieldAttributes': [
        ]
    }
}
