# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_finalized_0_with_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'IDP',
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_finalized_1_without_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': None
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
                'finalHouseholdsListByTargetingCriteria'
            ]
        }
    ]
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_residence_status_0_with_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'HOST',
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_residence_status_1_without_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': None
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
                'finalHouseholdsListByTargetingCriteria'
            ]
        }
    ]
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_size_0_with_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'REFUGEE',
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_size_1_edit_0_with_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'HOST',
                        'size': 1
                    }
                },
                {
                    'node': {
                        'residenceStatus': 'IDP',
                        'size': 1
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_size_1_edit_1_without_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': None
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
                'finalHouseholdsListByTargetingCriteria'
            ]
        }
    ]
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_size_1_without_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': None
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
                'finalHouseholdsListByTargetingCriteria'
            ]
        }
    ]
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_size_2_edit_0_with_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'REFUGEE',
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_size_2_edit_1_without_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': None
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
                'finalHouseholdsListByTargetingCriteria'
            ]
        }
    ]
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_without_invalid_documents_0_with_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'HOST',
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_without_invalid_documents_1_without_permission 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': None
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
                'finalHouseholdsListByTargetingCriteria'
            ]
        }
    ]
}
