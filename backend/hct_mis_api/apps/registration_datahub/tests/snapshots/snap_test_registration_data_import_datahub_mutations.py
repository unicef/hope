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
                'numberOfIndividuals': 0
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubQuery::test_registration_data_import_create 1'] = {
    'data': {
        'createRegistrationDataImport': {
            'registrationDataImport': {
                'name': 'New Import of Data 123',
                'numberOfHouseholds': 500,
                'numberOfIndividuals': 1000,
                'status': 'IN_REVIEW'
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubQuery::test_approve_registration_data_import 1'] = {
    'data': {
        'approveRegistrationDataImport': {
            'registrationDataImport': {
                'status': 'APPROVED'
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubQuery::test_approve_registration_data_import_wrong_initial_status 1'] = {
    'data': {
        'approveRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Only In Review Registration Data Import can be Approved',
            'path': [
                'approveRegistrationDataImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportDatahubQuery::test_merge_registration_data_import 1'] = {
    'data': {
        'mergeRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Cannot assign "\'Lorem Ipsum\'": "Household.location" must be a "Location" instance.',
            'path': [
                'mergeRegistrationDataImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportDatahubMutations::test_merge_registration_data_import 1'] = {
    'data': {
        'mergeRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': '',
            'path': [
                'mergeRegistrationDataImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportDatahubMutations::test_approve_registration_data_import 1'] = {
    'data': {
        'approveRegistrationDataImport': {
            'registrationDataImport': {
                'status': 'APPROVED'
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_approve_registration_data_import_wrong_initial_status 1'] = {
    'data': {
        'approveRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Only In Review Registration Data Import can be Approved',
            'path': [
                'approveRegistrationDataImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_create 1'] = {
    'data': {
        'createRegistrationDataImport': {
            'registrationDataImport': {
                'name': 'New Import of Data 123',
                'numberOfHouseholds': 500,
                'numberOfIndividuals': 1000,
                'status': 'IN_REVIEW'
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_datahub_upload 1'] = {
    'data': {
        'uploadImportDataXlsxFile': {
            'importData': {
                'numberOfHouseholds': 0,
                'numberOfIndividuals': 0
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_unapprove_registration_data_import 1'] = {
    'data': {
        'unapproveRegistrationDataImport': {
            'registrationDataImport': {
                'status': 'IN_REVIEW'
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_unapprove_registration_data_import_wrong_initial_status 1'] = {
    'data': {
        'unapproveRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Only Approved Registration Data Import can be Unapproved',
            'path': [
                'unapproveRegistrationDataImport'
            ]
        }
    ]
}
