# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestIndividualQuery::test_individual_programme_filter 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
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
                },
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
                        'birthDate': '1962-08-07',
                        'familyName': 'Gibbs',
                        'givenName': 'Janet',
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
                        'phoneNo': '158-147-0749x340'
                    }
                },
                {
                    'node': {
                        'birthDate': '1939-12-16',
                        'familyName': 'Gomez',
                        'givenName': 'Roger',
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
                        'phoneNo': '+19542331272'
                    }
                },
                {
                    'node': {
                        'birthDate': '1977-08-06',
                        'familyName': 'Michael',
                        'givenName': 'Danielle',
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
                        'phoneNo': '001-291-293-0741x813'
                    }
                },
                {
                    'node': {
                        'birthDate': '1956-01-03',
                        'familyName': 'White',
                        'givenName': 'Travis',
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
                        'phoneNo': '488-733-5557x06643'
                    }
                },
                {
                    'node': {
                        'birthDate': '1933-07-10',
                        'familyName': 'French',
                        'givenName': 'Catherine',
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
                        'phoneNo': '001-321-086-1627x329'
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_individual_query_all 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1973-03-23',
                        'familyName': 'Torres',
                        'fullName': 'Eric Torres',
                        'givenName': 'Eric',
                        'phoneNo': '+12282315473'
                    }
                },
                {
                    'node': {
                        'birthDate': '1967-10-19',
                        'familyName': 'Barry',
                        'fullName': 'Katie Kristen Barry',
                        'givenName': 'Katie',
                        'phoneNo': '+12064930450'
                    }
                },
                {
                    'node': {
                        'birthDate': '1967-07-12',
                        'familyName': 'Davidson',
                        'fullName': 'Tara Lauren Davidson',
                        'givenName': 'Tara',
                        'phoneNo': '+18179547965'
                    }
                },
                {
                    'node': {
                        'birthDate': '2001-12-30',
                        'familyName': 'Livingston',
                        'fullName': 'Jesse Christopher Livingston',
                        'givenName': 'Jesse',
                        'phoneNo': '960-534-4074x3203'
                    }
                },
                {
                    'node': {
                        'birthDate': '1937-01-19',
                        'familyName': 'Sloan',
                        'fullName': 'Laura Carol Sloan',
                        'givenName': 'Laura',
                        'phoneNo': '+15394566371'
                    }
                },
                {
                    'node': {
                        'birthDate': '1945-04-30',
                        'familyName': 'Smith',
                        'fullName': 'Laura Elizabeth Smith',
                        'givenName': 'Laura',
                        'phoneNo': '(824)628-3298x64013'
                    }
                },
                {
                    'node': {
                        'birthDate': '1934-10-04',
                        'familyName': 'Sanford',
                        'fullName': 'Angela Christina Sanford',
                        'givenName': 'Angela',
                        'phoneNo': '496-383-7465x901'
                    }
                },
                {
                    'node': {
                        'birthDate': '1943-07-30',
                        'familyName': 'Butler',
                        'fullName': 'Benjamin Butler',
                        'givenName': 'Benjamin',
                        'phoneNo': '(953)682-4596'
                    }
                },
                {
                    'node': {
                        'birthDate': '1946-02-15',
                        'familyName': 'Ford',
                        'fullName': 'Robin Ford',
                        'givenName': 'Robin',
                        'phoneNo': '+18663567905'
                    }
                },
                {
                    'node': {
                        'birthDate': '1983-12-21',
                        'familyName': 'Perry',
                        'fullName': 'Timothy Perry',
                        'givenName': 'Timothy',
                        'phoneNo': '(548)313-1700-902'
                    }
                },
                {
                    'node': {
                        'birthDate': '1969-11-29',
                        'familyName': 'Franklin',
                        'fullName': 'Jenna Franklin',
                        'givenName': 'Jenna',
                        'phoneNo': '001-296-358-5428-607'
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_individual_query_single 1'] = {
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
