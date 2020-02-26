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
                        'dataSource': 'XLS',
                        'importedBy': 'Super User',
                        'name': 'Lorem Ipsum',
                        'status': 'IN_PROGRESS'
                    }
                },
                {
                    'node': {
                        'dataSource': 'XLS',
                        'importedBy': 'Super User',
                        'name': 'Lorem Ipsum 2',
                        'status': 'DONE'
                    }
                },
                {
                    'node': {
                        'dataSource': 'XLS',
                        'importedBy': 'Super User',
                        'name': 'Lorem Ipsum 3',
                        'status': 'IN_PROGRESS'
                    }
                }
            ]
        }
    }
}

snapshots['TestRegistrationDataImportDatahubQuery::test_registration_data_import_datahub_query_single 1'] = {
    'data': {
        'registrationDataImportDatahub': {
            'dataSource': 'XLS',
            'importedBy': 'Super User',
            'name': 'Lorem Ipsum',
            'status': 'IN_PROGRESS'
        }
    }
}
