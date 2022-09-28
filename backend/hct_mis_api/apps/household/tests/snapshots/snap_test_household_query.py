# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestHouseholdQuery::test_household_filter_by_programme_0_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'programs': {
                            'edges': [
                                {
                                    'node': {
                                        'name': 'Test program ONE'
                                    }
                                }
                            ]
                        },
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'programs': {
                            'edges': [
                                {
                                    'node': {
                                        'name': 'Test program ONE'
                                    }
                                }
                            ]
                        },
                        'size': 1
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'programs': {
                            'edges': [
                                {
                                    'node': {
                                        'name': 'Test program ONE'
                                    }
                                }
                            ]
                        },
                        'size': 11
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_filter_by_programme_1_without_permission 1'] = {
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

snapshots['TestHouseholdQuery::test_household_query_all_0_all_with_permission 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 1
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 5
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 11
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
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
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
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
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 5
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 11
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
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
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 1
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 2
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'Poland',
                        'size': 5
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_single_0_with_permission 1'] = {
    'data': {
        'household': {
            'address': 'Lorem Ipsum',
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
