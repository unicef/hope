# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestTargetPopulationQuery::test_all_target_population_query 1'] = {
    'data': {
        'allTargetPopulation': {
            'edges': [
                {
                    'node': {
                        'createdAt': '2020-03-06T12:59:43.310488',
                        'createdBy': {
                            'firstName': 'Karen',
                            'lastName': 'Callahan'
                        },
                        'households': [
                            {
                                'address': '''Unit 6543 Box 7148
DPO AE 13366''',
                                'familySize': 7,
                                'headOfHousehold': None,
                                'householdCaId': '379b9f87-847c-4de5-ac26-e6736eb35fd0',
                                'location': {
                                    'title': 'East Allenmouth'
                                },
                                'registrationDataImportId': {
                                    'name': 'Thank compare others light.'
                                }
                            },
                            {
                                'address': '''16962 Mccarty Grove
Whitneymouth, ID 31460''',
                                'familySize': 6,
                                'headOfHousehold': None,
                                'householdCaId': 'ca45e35b-eb96-4161-a2ea-25cf4876aaee',
                                'location': {
                                    'title': 'Vargasville'
                                },
                                'registrationDataImportId': {
                                    'name': 'Market begin us.'
                                }
                            },
                            {
                                'address': '''667 Erin Plains
Rebeccaborough, IN 64747''',
                                'familySize': 4,
                                'headOfHousehold': None,
                                'householdCaId': '02f6be12-e4f1-46f0-9636-c553d2274464',
                                'location': {
                                    'title': 'North Scott'
                                },
                                'registrationDataImportId': {
                                    'name': 'Choose if actually subject store visit under capital.'
                                }
                            },
                            {
                                'address': '''PSC 7831, Box 5100
APO AA 58378''',
                                'familySize': 5,
                                'headOfHousehold': None,
                                'householdCaId': 'c5b1a2b1-4c6e-4f49-92e8-4fe59ed9fa99',
                                'location': {
                                    'title': 'New Joshuatown'
                                },
                                'registrationDataImportId': {
                                    'name': 'How speak have east brother window.'
                                }
                            },
                            {
                                'address': '''6868 Jeremiah Hill Suite 979
South Ryan, VT 80457''',
                                'familySize': 6,
                                'headOfHousehold': None,
                                'householdCaId': '9e67b8cc-4a53-4019-804b-48699362d422',
                                'location': {
                                    'title': 'New Donna'
                                },
                                'registrationDataImportId': {
                                    'name': 'State doctor fire.'
                                }
                            }
                        ],
                        'lastEditedAt': '2020-03-06T12:59:43.321203',
                        'name': 'target_1',
                        'status': 'IN_PROGRESS'
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-03-06T12:59:43.322440',
                        'createdBy': {
                            'firstName': 'Karen',
                            'lastName': 'Callahan'
                        },
                        'households': [
                            {
                                'address': '''Unit 6543 Box 7148
DPO AE 13366''',
                                'familySize': 7,
                                'headOfHousehold': None,
                                'householdCaId': '379b9f87-847c-4de5-ac26-e6736eb35fd0',
                                'location': {
                                    'title': 'East Allenmouth'
                                },
                                'registrationDataImportId': {
                                    'name': 'Thank compare others light.'
                                }
                            },
                            {
                                'address': '''16962 Mccarty Grove
Whitneymouth, ID 31460''',
                                'familySize': 6,
                                'headOfHousehold': None,
                                'householdCaId': 'ca45e35b-eb96-4161-a2ea-25cf4876aaee',
                                'location': {
                                    'title': 'Vargasville'
                                },
                                'registrationDataImportId': {
                                    'name': 'Market begin us.'
                                }
                            },
                            {
                                'address': '''667 Erin Plains
Rebeccaborough, IN 64747''',
                                'familySize': 4,
                                'headOfHousehold': None,
                                'householdCaId': '02f6be12-e4f1-46f0-9636-c553d2274464',
                                'location': {
                                    'title': 'North Scott'
                                },
                                'registrationDataImportId': {
                                    'name': 'Choose if actually subject store visit under capital.'
                                }
                            },
                            {
                                'address': '''PSC 7831, Box 5100
APO AA 58378''',
                                'familySize': 5,
                                'headOfHousehold': None,
                                'householdCaId': 'c5b1a2b1-4c6e-4f49-92e8-4fe59ed9fa99',
                                'location': {
                                    'title': 'New Joshuatown'
                                },
                                'registrationDataImportId': {
                                    'name': 'How speak have east brother window.'
                                }
                            },
                            {
                                'address': '''6868 Jeremiah Hill Suite 979
South Ryan, VT 80457''',
                                'familySize': 6,
                                'headOfHousehold': None,
                                'householdCaId': '9e67b8cc-4a53-4019-804b-48699362d422',
                                'location': {
                                    'title': 'New Donna'
                                },
                                'registrationDataImportId': {
                                    'name': 'State doctor fire.'
                                }
                            }
                        ],
                        'lastEditedAt': '2020-03-06T12:59:43.331441',
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
            'createdAt': '2020-03-06T12:59:43.310488',
            'createdBy': {
                'firstName': 'Karen',
                'lastName': 'Callahan'
            },
            'households': [
                {
                    'address': '''Unit 6543 Box 7148
DPO AE 13366''',
                    'familySize': 7,
                    'headOfHousehold': None,
                    'householdCaId': '379b9f87-847c-4de5-ac26-e6736eb35fd0',
                    'location': {
                        'title': 'East Allenmouth'
                    },
                    'registrationDataImportId': {
                        'name': 'Thank compare others light.'
                    }
                },
                {
                    'address': '''16962 Mccarty Grove
Whitneymouth, ID 31460''',
                    'familySize': 6,
                    'headOfHousehold': None,
                    'householdCaId': 'ca45e35b-eb96-4161-a2ea-25cf4876aaee',
                    'location': {
                        'title': 'Vargasville'
                    },
                    'registrationDataImportId': {
                        'name': 'Market begin us.'
                    }
                },
                {
                    'address': '''667 Erin Plains
Rebeccaborough, IN 64747''',
                    'familySize': 4,
                    'headOfHousehold': None,
                    'householdCaId': '02f6be12-e4f1-46f0-9636-c553d2274464',
                    'location': {
                        'title': 'North Scott'
                    },
                    'registrationDataImportId': {
                        'name': 'Choose if actually subject store visit under capital.'
                    }
                },
                {
                    'address': '''PSC 7831, Box 5100
APO AA 58378''',
                    'familySize': 5,
                    'headOfHousehold': None,
                    'householdCaId': 'c5b1a2b1-4c6e-4f49-92e8-4fe59ed9fa99',
                    'location': {
                        'title': 'New Joshuatown'
                    },
                    'registrationDataImportId': {
                        'name': 'How speak have east brother window.'
                    }
                },
                {
                    'address': '''6868 Jeremiah Hill Suite 979
South Ryan, VT 80457''',
                    'familySize': 6,
                    'headOfHousehold': None,
                    'householdCaId': '9e67b8cc-4a53-4019-804b-48699362d422',
                    'location': {
                        'title': 'New Donna'
                    },
                    'registrationDataImportId': {
                        'name': 'State doctor fire.'
                    }
                }
            ],
            'lastEditedAt': '2020-03-06T12:59:43.321203',
            'name': 'target_1',
            'status': 'IN_PROGRESS'
        }
    }
}
