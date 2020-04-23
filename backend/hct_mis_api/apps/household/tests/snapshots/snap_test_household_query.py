# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestHouseholdQuery::test_household_filter_by_programme 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
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
                        'countryOrigin': 'PL',
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
                        'countryOrigin': 'PL',
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

snapshots['TestHouseholdQuery::test_household_query_all 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 1
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 2
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 5
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 11
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 14
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_all_max 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 1
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 2
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 5
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_all_min 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 5
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 11
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 14
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_all_range 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 3
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 4
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'countryOrigin': 'PL',
                        'size': 5
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_query_single 1'] = {
    'data': {
        'household': {
            'address': 'Lorem Ipsum',
            'countryOrigin': 'PL',
            'size': 2
        }
    }
}
