# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestRegistrationDataImportQuery::test_registration_data_import_datahub_query_all_0_with_permission 1'] = {
    'data': {
        'allRegistrationDataImports': {
            'edges': [
                {
                    'node': {
                        'batchDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'batchUniqueCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'biometricDeduplicationEnabled': False,
                        'canMerge': False,
                        'dataSource': 'XLS',
                        'goldenRecordDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'goldenRecordPossibleDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'goldenRecordUniqueCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'biometricDeduplicated': 'NO',
                        'name': 'Lorem Ipsum 4',
                        'numberOfHouseholds': 184,
                        'numberOfIndividuals': 423,
                        'status': 'IN_REVIEW',
                        'totalHouseholdsCountWithValidPhoneNo': 0
                    }
                },
                {
                    'node': {
                        'batchDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            },
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'batchUniqueCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            },
                            {
                                'count': 323,
                                'percentage': 100.0
                            }
                        ],
                        'biometricDeduplicationEnabled': True,
                        'canMerge': False,
                        'dataSource': 'XLS',
                        'goldenRecordDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'goldenRecordPossibleDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            },
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'goldenRecordUniqueCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            },
                            {
                                'count': 323,
                                'percentage': 100.0
                            }
                        ],
                        'biometricDeduplicated': 'NO',
                        'name': 'Lorem Ipsum 3',
                        'numberOfHouseholds': 154,
                        'numberOfIndividuals': 323,
                        'status': 'IN_REVIEW',
                        'totalHouseholdsCountWithValidPhoneNo': 0
                    }
                },
                {
                    'node': {
                        'batchDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            },
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'batchUniqueCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            },
                            {
                                'count': 323,
                                'percentage': 100.0
                            }
                        ],
                        'biometricDeduplicationEnabled': True,
                        'canMerge': False,
                        'dataSource': 'XLS',
                        'goldenRecordDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'goldenRecordPossibleDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            },
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'goldenRecordUniqueCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            },
                            {
                                'count': 323,
                                'percentage': 100.0
                            }
                        ],
                        'biometricDeduplicated': 'YES',
                        'name': 'Lorem Ipsum 2',
                        'numberOfHouseholds': 154,
                        'numberOfIndividuals': 323,
                        'status': 'IN_REVIEW',
                        'totalHouseholdsCountWithValidPhoneNo': 0
                    }
                },
                {
                    'node': {
                        'batchDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'batchUniqueCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'biometricDeduplicationEnabled': False,
                        'canMerge': True,
                        'dataSource': 'XLS',
                        'goldenRecordDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'goldenRecordPossibleDuplicatesCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'goldenRecordUniqueCountAndPercentage': [
                            {
                                'count': 0,
                                'percentage': 0.0
                            }
                        ],
                        'biometricDeduplicated': 'NO',
                        'name': 'Lorem Ipsum',
                        'numberOfHouseholds': 54,
                        'numberOfIndividuals': 123,
                        'status': 'IN_REVIEW',
                        'totalHouseholdsCountWithValidPhoneNo': 0
                    }
                }
            ]
        }
    }
}

snapshots['TestRegistrationDataImportQuery::test_registration_data_import_datahub_query_all_1_without_permission 1'] = {
    'data': {
        'allRegistrationDataImports': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allRegistrationDataImports'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportQuery::test_registration_data_import_datahub_query_single_with_permission_0_with_permission 1'] = {
    'data': {
        'registrationDataImport': {
            'dataSource': 'XLS',
            'name': 'Lorem Ipsum',
            'numberOfHouseholds': 54,
            'numberOfIndividuals': 123,
            'status': 'IN_REVIEW'
        }
    }
}

snapshots['TestRegistrationDataImportQuery::test_registration_data_import_datahub_query_single_with_permission_1_without_permission 1'] = {
    'data': {
        'registrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'registrationDataImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportQuery::test_registration_data_status_choices 1'] = {
    'data': {
        'registrationDataStatusChoices': [
            {
                'name': 'Deduplication',
                'value': 'DEDUPLICATION'
            },
            {
                'name': 'Deduplication Failed',
                'value': 'DEDUPLICATION_FAILED'
            },
            {
                'name': 'Import Error',
                'value': 'IMPORT_ERROR'
            },
            {
                'name': 'Import Scheduled',
                'value': 'IMPORT_SCHEDULED'
            },
            {
                'name': 'Importing',
                'value': 'IMPORTING'
            },
            {
                'name': 'In Review',
                'value': 'IN_REVIEW'
            },
            {
                'name': 'Loading',
                'value': 'LOADING'
            },
            {
                'name': 'Merge Error',
                'value': 'MERGE_ERROR'
            },
            {
                'name': 'Merge Scheduled',
                'value': 'MERGE_SCHEDULED'
            },
            {
                'name': 'Merged',
                'value': 'MERGED'
            },
            {
                'name': 'Merging',
                'value': 'MERGING'
            },
            {
                'name': 'Refused import',
                'value': 'REFUSED'
            }
        ]
    }
}
