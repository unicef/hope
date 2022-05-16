# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersOtherQueryTestCase::test_golden_record_by_targeting_criteria_bank_account_info 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'id': 'SW5kaXZpZHVhbE5vZGU6ODQzMTY0ZjAtZjhjYy00NTkwLWE4MDYtODBlMTM5ZTk4NDVh',
                                        'maritalStatus': 'SEPARATED',
                                        'phoneNo': '+48123456789',
                                        'sex': 'FEMALE'
                                    }
                                },
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'id': 'SW5kaXZpZHVhbE5vZGU6MzUwMzJkYzYtNmFmZS00MTQ4LWExM2EtNWI3M2U1MmVlYzJk',
                                        'maritalStatus': 'WIDOWED',
                                        'phoneNo': '+48 987654321',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 2
                    }
                },
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'id': 'SW5kaXZpZHVhbE5vZGU6ZWJkMTQ4MzItMmY5NS00NTY2LWEwYTItY2VhOWQ4OTZlZDQ0',
                                        'maritalStatus': 'MARRIED',
                                        'phoneNo': '',
                                        'sex': 'MALE'
                                    }
                                },
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'type': {
                                                            'type': 'TAX_ID'
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        'id': 'SW5kaXZpZHVhbE5vZGU6ODRlNDY5NTYtMTE2Yi00OGYwLWFlZWQtNTk3NDQ1Zjc1OWZm',
                                        'maritalStatus': 'DIVORCED',
                                        'phoneNo': '',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 2
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersOtherQueryTestCase::test_golden_record_by_targeting_criteria_has_bank_account_info 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'bankAccountInfo': {
                                            'bankName': 'Santander'
                                        },
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'maritalStatus': 'SINGLE',
                                        'phoneNo': '',
                                        'sex': 'FEMALE'
                                    }
                                },
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'type': {
                                                            'type': 'TAX_ID'
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        'maritalStatus': 'DIVORCED',
                                        'phoneNo': '',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersOtherQueryTestCase::test_golden_record_by_targeting_criteria_has_not_bank_account_info 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'maritalStatus': 'SEPARATED',
                                        'phoneNo': '+48123456789',
                                        'sex': 'FEMALE'
                                    }
                                },
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'maritalStatus': 'A_',
                                        'phoneNo': '+48 987654321',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 2
                    }
                },
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'bankAccountInfo': {
                                            'bankName': 'Santander'
                                        },
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'maritalStatus': 'SINGLE',
                                        'phoneNo': '',
                                        'sex': 'FEMALE'
                                    }
                                },
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'type': {
                                                            'type': 'TAX_ID'
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        'maritalStatus': 'DIVORCED',
                                        'phoneNo': '',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 2
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersOtherQueryTestCase::test_golden_record_by_targeting_criteria_phone_number 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'maritalStatus': 'SEPARATED',
                                        'phoneNo': '+48123456789',
                                        'sex': 'FEMALE'
                                    }
                                },
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'maritalStatus': 'A_',
                                        'phoneNo': '+48 987654321',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersOtherQueryTestCase::test_golden_record_by_targeting_criteria_tax_id 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'bankAccountInfo': {
                                            'bankName': 'Santander'
                                        },
                                        'documents': {
                                            'edges': [
                                            ]
                                        },
                                        'maritalStatus': 'SINGLE',
                                        'phoneNo': '',
                                        'sex': 'FEMALE'
                                    }
                                },
                                {
                                    'node': {
                                        'bankAccountInfo': None,
                                        'documents': {
                                            'edges': [
                                                {
                                                    'node': {
                                                        'type': {
                                                            'type': 'TAX_ID'
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        'maritalStatus': 'DIVORCED',
                                        'phoneNo': '',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase::test_golden_record_by_targeting_criteria_observed_disability 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'maritalStatus': 'MARRIED',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase::test_golden_record_by_targeting_criteria_observed_disability_with_invalid_argument 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
            ],
            'totalCount': 0
        }
    }
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase::test_golden_record_by_targeting_criteria_size 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'maritalStatus': 'MARRIED',
                                        'sex': 'MALE'
                                    }
                                }
                            ]
                        },
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    }
}
