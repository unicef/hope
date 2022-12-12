# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersOtherQueryTestCase::test_golden_record_by_targeting_criteria_has_bank_account_info 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': None,
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 17,
                    'line': 8
                }
            ],
            'message': 'BusinessArea matching query does not exist.',
            'path': [
                'goldenRecordByTargetingCriteria',
                'edges',
                0,
                'node',
                'individuals'
            ]
        }
    ]
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersOtherQueryTestCase::test_golden_record_by_targeting_criteria_has_not_bank_account_info 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': None,
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 17,
                    'line': 8
                }
            ],
            'message': 'BusinessArea matching query does not exist.',
            'path': [
                'goldenRecordByTargetingCriteria',
                'edges',
                0,
                'node',
                'individuals'
            ]
        }
    ]
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersOtherQueryTestCase::test_golden_record_by_targeting_criteria_phone_number 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': None,
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 17,
                    'line': 8
                }
            ],
            'message': 'BusinessArea matching query does not exist.',
            'path': [
                'goldenRecordByTargetingCriteria',
                'edges',
                0,
                'node',
                'individuals'
            ]
        }
    ]
}

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersOtherQueryTestCase::test_golden_record_by_targeting_criteria_tax_id 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': None,
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 17,
                    'line': 8
                }
            ],
            'message': 'BusinessArea matching query does not exist.',
            'path': [
                'goldenRecordByTargetingCriteria',
                'edges',
                0,
                'node',
                'individuals'
            ]
        }
    ]
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
                },
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'maritalStatus': 'MARRIED',
                                        'sex': 'FEMALE'
                                    }
                                },
                                {
                                    'node': {
                                        'maritalStatus': 'SINGLE',
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

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase::test_golden_record_by_targeting_criteria_observed_disability_with_valid_argument 1'] = {
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
                },
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'maritalStatus': 'MARRIED',
                                        'sex': 'FEMALE'
                                    }
                                },
                                {
                                    'node': {
                                        'maritalStatus': 'SINGLE',
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
