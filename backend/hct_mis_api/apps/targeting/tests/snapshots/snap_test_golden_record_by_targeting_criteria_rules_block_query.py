# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase::test_golden_record_by_targeting_criteria_bank_account_info 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'maritalStatus': 'SINGLE',
                                        'sex': 'MALE'
                                    }
                                },
                                {
                                    'node': {
                                        'maritalStatus': 'MARRIED',
                                        'sex': 'FEMALE'
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
            'totalCount': 2
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

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase::test_golden_record_by_targeting_criteria_phone_number 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'individuals': {
                            'edges': [
                                {
                                    'node': {
                                        'maritalStatus': 'SINGLE',
                                        'sex': 'MALE'
                                    }
                                },
                                {
                                    'node': {
                                        'maritalStatus': 'MARRIED',
                                        'sex': 'FEMALE'
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

snapshots['GoldenRecordTargetingCriteriaWithBlockFiltersQueryTestCase::test_golden_record_by_targeting_criteria_tax_id 1'] = {
    'data': {
        'goldenRecordByTargetingCriteria': {
            'edges': [
            ],
            'totalCount': 0
        }
    }
}
