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

snapshots['TestIndividualQuery::test_individual_query_single_0_with_permission 1'] = {
    'data': {
        'individual': {
            'birthDate': '1943-07-30',
            'familyName': 'Butler',
            'fullName': 'Benjamin Butler',
            'givenName': 'Benjamin',
            'phoneNo': '(953)682-4596'
        }
    }
}

snapshots['TestIndividualQuery::test_individual_query_single_1_without_permission 1'] = {
    'data': {
        'individual': None
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
                'individual'
            ]
        }
    ]
}
