# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_datahub_upload 1'] = {
    'data': {
        'uploadImportDataXlsxFile': {
            'errors': [
            ],
            'importData': {
                'numberOfHouseholds': 19,
                'numberOfIndividuals': 27
            }
        }
    }
}
