# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestHouseholdQuery::test_household_query_all_0_all_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 2',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 3',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 5',
                        'countryOrigin': 'Poland',
                        'size': 5
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 14',
                        'countryOrigin': 'Poland',
                        'size': 14
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_all_1_all_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_household_query_all_2_all_range_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 3',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 5',
                        'countryOrigin': 'Poland',
                        'size': 5
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_all_3_all_range_without_permission 1'] = {
    'data': {
        'allHouseholds': None
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
                'allHouseholds'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_household_query_all_4_all_min_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 3',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 5',
                        'countryOrigin': 'Poland',
                        'size': 5
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 14',
                        'countryOrigin': 'Poland',
                        'size': 14
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_all_5_all_max_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 2',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 3',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 5',
                        'countryOrigin': 'Poland',
                        'size': 5
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_all_for_all_programs 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 1',
                        'countryOrigin': 'Poland',
                        'size': 1
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 2',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 3',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 4',
                        'countryOrigin': 'Poland',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 5',
                        'countryOrigin': 'Poland',
                        'size': 5
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 11',
                        'countryOrigin': 'Poland',
                        'size': 11
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum 14',
                        'countryOrigin': 'Poland',
                        'size': 14
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_all_for_all_programs_user_with_no_program_access 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_draft 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_single_0_with_permission 1'] = {
    'data': {
        'household': {
            'address': 'Lorem Ipsum 2',
            'admin1': {
                'pCode': 'area1'
            },
            'admin2': {
                'pCode': 'area2'
            },
            'adminArea': {
                'pCode': 'area2'
            },
            'adminAreaTitle': 'City Test2 - area2',
            'countryOrigin': 'Poland',
            'size': 2
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_single_1_without_permission 1'] = {
    'data': {
        'household': None
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
                'household'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_household_query_single_different_program_in_header 1'] = {
    'data': {
        'household': None
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
                'household'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_household_query_single_import_id_0 1'] = {
    'data': {
        'household': {
            'importId': 'HH-123123'
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_single_import_id_1_detail_id 1'] = {
    'data': {
        'household': {
            'importId': 'HH-123123 (Detail id test1)'
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_single_import_id_2_enumerator_rec_id 1'] = {
    'data': {
        'household': {
            'importId': 'HH-123123 (Enumerator ID 123)'
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_by_national_id_no_filter_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 2',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_by_national_id_no_filter_1_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_query_households_by_detail_id_filter_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 2',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_by_detail_id_filter_1_with_permission_wrong_type_in_search 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_by_detail_id_filter_2_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_query_households_by_search_full_name_filter_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 2',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_by_search_full_name_filter_1_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_query_households_by_search_household_id_filter_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 2',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_by_search_household_id_filter_1_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_query_households_by_search_individual_id_filter_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 2',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_by_search_individual_id_filter_1_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_query_households_by_search_phone_no_filter_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum 2',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_by_search_phone_no_filter_1_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_query_households_search_incorrect_kobo_asset_id_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_search_incorrect_kobo_asset_id_1_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}

snapshots['TestHouseholdQuery::test_query_households_search_without_search_type_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_query_households_search_without_search_type_1_without_permission 1'] = {
    'data': {
        'allHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allHouseholds'
            ]
        }
    ]
}
