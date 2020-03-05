# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestHouseholdQuery::test_household_query_all 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 2,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 4,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 5,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 1,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 3,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 11,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 14,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
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
                        'familySize': 2,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 4,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 5,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 1,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 3,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
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
                        'familySize': 4,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 5,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 3,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 11,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 14,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
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
                        'familySize': 4,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 5,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 3,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL'
                    }
                }
            ]
        }
    }
}

snapshots['TestHouseholdQuery::test_household_filter_by_programme 1'] = {
    'data': {
        'allHouseholds': {
            'edges': [
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 2,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL',
                        'programs': {
                            'edges': [
                                {
                                    'node': {
                                        'name': 'Test program TWO'
                                    }
                                }
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 5,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL',
                        'programs': {
                            'edges': [
                                {
                                    'node': {
                                        'name': 'Test program TWO'
                                    }
                                }
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 3,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL',
                        'programs': {
                            'edges': [
                                {
                                    'node': {
                                        'name': 'Test program TWO'
                                    }
                                }
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'address': 'Lorem Ipsum',
                        'familySize': 14,
                        'householdCaId': '123-123-123',
                        'nationality': 'PL',
                        'programs': {
                            'edges': [
                                {
                                    'node': {
                                        'name': 'Test program TWO'
                                    }
                                }
                            ]
                        }
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
            'familySize': 2,
            'householdCaId': '123-123-123',
            'nationality': 'PL'
        }
    }
}
