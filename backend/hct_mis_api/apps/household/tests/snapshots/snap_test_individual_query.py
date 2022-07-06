# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestIndividualQuery::test_individual_programme_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1943-07-30',
                        'familyName': 'Butler',
                        'givenName': 'Benjamin',
                        'household': {
                            'programs': {
                                'edges': [
                                    {
                                        'node': {
                                            'name': 'Test program TWO'
                                        }
                                    }
                                ]
                            }
                        },
                        'phoneNo': '(953)682-4596'
                    }
                },
                {
                    'node': {
                        'birthDate': '1969-11-29',
                        'familyName': 'Franklin',
                        'givenName': 'Jenna',
                        'household': {
                            'programs': {
                                'edges': [
                                    {
                                        'node': {
                                            'name': 'Test program TWO'
                                        }
                                    }
                                ]
                            }
                        },
                        'phoneNo': '001-296-358-5428-607'
                    }
                },
                {
                    'node': {
                        'birthDate': '1983-12-21',
                        'familyName': 'Perry',
                        'givenName': 'Timothy',
                        'household': {
                            'programs': {
                                'edges': [
                                    {
                                        'node': {
                                            'name': 'Test program TWO'
                                        }
                                    }
                                ]
                            }
                        },
                        'phoneNo': '(548)313-1700-902'
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_individual_programme_filter_1_without_permission 1'] = {
    'data': {
        'allIndividuals': None
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
                'allIndividuals'
            ]
        }
    ]
}

snapshots['TestIndividualQuery::test_individual_query_all_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1969-11-29',
                        'familyName': 'Franklin',
                        'fullName': 'Jenna Franklin',
                        'givenName': 'Jenna',
                        'phoneNo': '001-296-358-5428-607',
                        'phoneNoValid': False
                    }
                },
                {
                    'node': {
                        'birthDate': '1973-03-23',
                        'familyName': 'Torres',
                        'fullName': 'Eric Torres',
                        'givenName': 'Eric',
                        'phoneNo': '+12282315473',
                        'phoneNoValid': True
                    }
                },
                {
                    'node': {
                        'birthDate': '1946-02-15',
                        'familyName': 'Ford',
                        'fullName': 'Robin Ford',
                        'givenName': 'Robin',
                        'phoneNo': '+18663567905',
                        'phoneNoValid': True
                    }
                },
                {
                    'node': {
                        'birthDate': '1983-12-21',
                        'familyName': 'Perry',
                        'fullName': 'Timothy Perry',
                        'givenName': 'Timothy',
                        'phoneNo': '(548)313-1700-902',
                        'phoneNoValid': False
                    }
                },
                {
                    'node': {
                        'birthDate': '1943-07-30',
                        'familyName': 'Butler',
                        'fullName': 'Benjamin Butler',
                        'givenName': 'Benjamin',
                        'phoneNo': '(953)682-4596',
                        'phoneNoValid': False
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_individual_query_all_1_without_permission 1'] = {
    'data': {
        'allIndividuals': None
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
                'allIndividuals'
            ]
        }
    ]
}

snapshots['TestIndividualQuery::test_individual_query_single_0_with_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 27,
                    'line': 3
                }
            ],
            'message': 'Unknown argument "orderBy" on field "individual" of type "Query".'
        }
    ]
}

snapshots['TestIndividualQuery::test_individual_query_single_1_without_permission 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 27,
                    'line': 3
                }
            ],
            'message': 'Unknown argument "orderBy" on field "individual" of type "Query".'
        }
    ]
}

snapshots['TestIndividualQuery::test_query_individuals_by_search_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1969-11-29',
                        'familyName': 'Franklin',
                        'fullName': 'Jenna Franklin',
                        'givenName': 'Jenna',
                        'phoneNo': '001-296-358-5428-607',
                        'phoneNoValid': False
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_query_individuals_by_search_filter_1_without_permission 1'] = {
    'data': {
        'allIndividuals': None
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
                'allIndividuals'
            ]
        }
    ]
}
