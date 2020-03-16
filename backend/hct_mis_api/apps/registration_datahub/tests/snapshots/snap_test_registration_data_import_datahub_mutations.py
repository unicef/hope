# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestRegistrationDataImportDatahubQuery::test_registration_data_import_datahub_upload 1'] = {
    'data': {
        'uploadImportDataXlsxFile': {
            'importData': {
                'numberOfHouseholds': 0,
                'numberOfIndividuals': 0,
                'xlsxFile': 'Registration_Data_Import_XLS_Template.xlsx'
            }
        }
    }
}
