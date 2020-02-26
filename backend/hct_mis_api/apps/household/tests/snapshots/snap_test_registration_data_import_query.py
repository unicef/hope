# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestRegistrationDataImportQuery::test_registration_data_import_datahub_query_all 1'] = {
    'data': {
        'allRegistrationDataImports': {
            'edges': [
                {
                    'node': {
                        'dataSource': 'XLS',
                        'name': 'Lorem Ipsum',
                        'numberOfHouseholds': 54,
                        'numberOfIndividuals': 123,
                        'status': 'IN_PROGRESS'
                    }
                },
                {
                    'node': {
                        'dataSource': 'XLS',
                        'name': 'Lorem Ipsum 2',
                        'numberOfHouseholds': 154,
                        'numberOfIndividuals': 323,
                        'status': 'DONE'
                    }
                },
                {
                    'node': {
                        'dataSource': 'XLS',
                        'name': 'Lorem Ipsum 3',
                        'numberOfHouseholds': 184,
                        'numberOfIndividuals': 423,
                        'status': 'IN_PROGRESS'
                    }
                }
            ]
        }
    }
}

snapshots['TestRegistrationDataImportQuery::test_registration_data_import_datahub_query_single 1'] = {
    'data': {
        'registrationDataImport': {
            'dataSource': 'XLS',
            'name': 'Lorem Ipsum',
            'numberOfHouseholds': 54,
            'numberOfIndividuals': 123,
            'status': 'IN_PROGRESS'
        }
    }
}
