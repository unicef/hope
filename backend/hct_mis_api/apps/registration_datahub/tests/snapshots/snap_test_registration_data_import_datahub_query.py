# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestRegistrationDataImportDatahubQuery::test_registration_data_import_datahub_query_all 1'] = {
    'data': {
        'allRegistrationDataImportsDatahub': {
            'edges': [
                {
                    'node': {
                        'hctId': '42191234-5a31-11ea-82b4-0242ac130003',
                        'name': 'Lorem Ipsum'
                    }
                },
                {
                    'node': {
                        'hctId': 'c2abeded-4aa0-422a-bfa2-b18dec20071f',
                        'name': 'Lorem Ipsum 2'
                    }
                },
                {
                    'node': {
                        'hctId': 'df7e419f-26bd-4a52-8698-0a201447a5f1',
                        'name': 'Lorem Ipsum 3'
                    }
                }
            ]
        }
    }
}

snapshots['TestRegistrationDataImportDatahubQuery::test_registration_data_import_datahub_query_single 1'] = {
    'data': {
        'registrationDataImportDatahub': {
            'hctId': '42191234-5a31-11ea-82b4-0242ac130003',
            'name': 'Lorem Ipsum'
        }
    }
}
