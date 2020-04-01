# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestTargetStatusTypesQuery::test_target_status_types_query 1'] = {
    'data': {
        'targetStatusTypes': [
            {
                'key': 'IN_PROGRESS',
                'value': 'In Progress'
            },
            {
                'key': 'FINALIZED',
                'value': 'Finalized'
            }
        ]
    }
}

snapshots['TestTargetPopulationQuery::test_all_target_population_num_individuals_query 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_all_target_population_query 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'createdAt': '2020-03-23T19:57:05.036492',
                        'createdBy': {
                            'firstName': 'Ivan',
                            'lastName': 'Martin'
                        },
                        'households': {
                            'edges': [
                                {
                                    'node': {
                                        'address': '''65807 Price Tunnel Apt. 450
Zacharyport, NV 18878''',
                                        'familySize': 4,
                                        'headOfHousehold': None,
                                        'householdCaId': '5ca093b9-0170-4711-8228-d886e822bd6f',
                                        'location': {
                                            'title': 'Toddfurt'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Make identify lawyer degree case.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''96389 Brooks Throughway Suite 346
Lake Alyssafort, IN 34678''',
                                        'familySize': 6,
                                        'headOfHousehold': None,
                                        'householdCaId': '11a351e5-771c-48e4-bf76-81cedc596e6c',
                                        'location': {
                                            'title': 'Jenniferhaven'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Study turn air movie.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''763 Leslie Cape Suite 079
Christinahaven, LA 23524''',
                                        'familySize': 6,
                                        'headOfHousehold': None,
                                        'householdCaId': 'ea5dccfd-d551-408b-a6b2-8064d74805ab',
                                        'location': {
                                            'title': 'Robinsonview'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Movie quality marriage happen have range.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''1154 Jones Radial Apt. 441
West Josefort, CO 25293''',
                                        'familySize': 3,
                                        'headOfHousehold': None,
                                        'householdCaId': '278de70a-1f7d-46cd-a4d2-dc2278a90de5',
                                        'location': {
                                            'title': 'East Joshuamouth'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Box enough civil tell whose response to.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''4746 Braun Ridges Suite 127
New Ashley, NC 65820''',
                                        'familySize': 4,
                                        'headOfHousehold': None,
                                        'householdCaId': '5c0dcc3e-410d-4741-96ae-a71581ef548e',
                                        'location': {
                                            'title': 'Christineland'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Send perform final begin especially director popular.'
                                        }
                                    }
                                }
                            ]
                        },
                        'lastEditedAt': '2020-03-23T19:57:05.046425',
                        'name': 'target_1',
                        'status': 'FINALIZED'
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-03-23T19:57:05.047670',
                        'createdBy': {
                            'firstName': 'Ivan',
                            'lastName': 'Martin'
                        },
                        'households': {
                            'edges': [
                                {
                                    'node': {
                                        'address': '''65807 Price Tunnel Apt. 450
Zacharyport, NV 18878''',
                                        'familySize': 4,
                                        'headOfHousehold': None,
                                        'householdCaId': '5ca093b9-0170-4711-8228-d886e822bd6f',
                                        'location': {
                                            'title': 'Toddfurt'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Make identify lawyer degree case.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''96389 Brooks Throughway Suite 346
Lake Alyssafort, IN 34678''',
                                        'familySize': 6,
                                        'headOfHousehold': None,
                                        'householdCaId': '11a351e5-771c-48e4-bf76-81cedc596e6c',
                                        'location': {
                                            'title': 'Jenniferhaven'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Study turn air movie.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''763 Leslie Cape Suite 079
Christinahaven, LA 23524''',
                                        'familySize': 6,
                                        'headOfHousehold': None,
                                        'householdCaId': 'ea5dccfd-d551-408b-a6b2-8064d74805ab',
                                        'location': {
                                            'title': 'Robinsonview'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Movie quality marriage happen have range.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''1154 Jones Radial Apt. 441
West Josefort, CO 25293''',
                                        'familySize': 3,
                                        'headOfHousehold': None,
                                        'householdCaId': '278de70a-1f7d-46cd-a4d2-dc2278a90de5',
                                        'location': {
                                            'title': 'East Joshuamouth'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Box enough civil tell whose response to.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''4746 Braun Ridges Suite 127
New Ashley, NC 65820''',
                                        'familySize': 4,
                                        'headOfHousehold': None,
                                        'householdCaId': '5c0dcc3e-410d-4741-96ae-a71581ef548e',
                                        'location': {
                                            'title': 'Christineland'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Send perform final begin especially director popular.'
                                        }
                                    }
                                }
                            ]
                        },
                        'lastEditedAt': '2020-03-23T19:57:05.056654',
                        'name': 'target_2',
                        'status': 'IN_PROGRESS'
                    }
                }
            ]
        }
    }
}

snapshots['TestTargetPopulationQuery::test_target_population_query 1'] = {
    'data': {
        'targetPopulation': {
            'createdAt': '2020-03-23T19:57:05.036492',
            'createdBy': {
                'firstName': 'Ivan',
                'lastName': 'Martin'
            },
            'households': {
                'edges': [
                    {
                        'node': {
                            'address': '''65807 Price Tunnel Apt. 450
Zacharyport, NV 18878''',
                            'familySize': 4,
                            'headOfHousehold': None,
                            'householdCaId': '5ca093b9-0170-4711-8228-d886e822bd6f',
                            'location': {
                                'title': 'Toddfurt'
                            },
                            'registrationDataImportId': {
                                'name': 'Make identify lawyer degree case.'
                            }
                        }
                    },
                    {
                        'node': {
                            'address': '''96389 Brooks Throughway Suite 346
Lake Alyssafort, IN 34678''',
                            'familySize': 6,
                            'headOfHousehold': None,
                            'householdCaId': '11a351e5-771c-48e4-bf76-81cedc596e6c',
                            'location': {
                                'title': 'Jenniferhaven'
                            },
                            'registrationDataImportId': {
                                'name': 'Study turn air movie.'
                            }
                        }
                    },
                    {
                        'node': {
                            'address': '''763 Leslie Cape Suite 079
Christinahaven, LA 23524''',
                            'familySize': 6,
                            'headOfHousehold': None,
                            'householdCaId': 'ea5dccfd-d551-408b-a6b2-8064d74805ab',
                            'location': {
                                'title': 'Robinsonview'
                            },
                            'registrationDataImportId': {
                                'name': 'Movie quality marriage happen have range.'
                            }
                        }
                    },
                    {
                        'node': {
                            'address': '''1154 Jones Radial Apt. 441
West Josefort, CO 25293''',
                            'familySize': 3,
                            'headOfHousehold': None,
                            'householdCaId': '278de70a-1f7d-46cd-a4d2-dc2278a90de5',
                            'location': {
                                'title': 'East Joshuamouth'
                            },
                            'registrationDataImportId': {
                                'name': 'Box enough civil tell whose response to.'
                            }
                        }
                    },
                    {
                        'node': {
                            'address': '''4746 Braun Ridges Suite 127
New Ashley, NC 65820''',
                            'familySize': 4,
                            'headOfHousehold': None,
                            'householdCaId': '5c0dcc3e-410d-4741-96ae-a71581ef548e',
                            'location': {
                                'title': 'Christineland'
                            },
                            'registrationDataImportId': {
                                'name': 'Send perform final begin especially director popular.'
                            }
                        }
                    }
                ]
            },
            'lastEditedAt': '2020-03-23T19:57:05.046425',
            'name': 'target_1',
            'status': 'FINALIZED'
        }
    }
}
