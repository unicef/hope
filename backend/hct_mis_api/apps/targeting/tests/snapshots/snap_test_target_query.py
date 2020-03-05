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
                        'createdAt': '2020-03-03T18:04:20.704217',
                        'createdBy': {
                            'firstName': 'Erik',
                            'lastName': 'Clayton'
                        },
                        'households': [
                            {
                                'address': '''4272 Mark Corner Apt. 467
Haydenville, OH 07388''',
                                'familySize': 7,
                                'headOfHousehold': None,
                                'householdCaId': '68ebca0a-8210-4e5d-8a76-8591502a3a14',
                                'location': {
                                    'title': 'East Vanessa'
                                },
                                'registrationDataImportId': {
                                    'name': 'Home seat central tax.'
                                }
                            },
                            {
                                'address': '''933 Kim Ridges Apt. 258
Nicholasberg, DE 44958''',
                                'familySize': 8,
                                'headOfHousehold': None,
                                'householdCaId': 'a8c8fc5c-c931-402a-a85e-e1e5ef27acb1',
                                'location': {
                                    'title': 'Lake Franktown'
                                },
                                'registrationDataImportId': {
                                    'name': 'Into bit nation senior value feeling.'
                                }
                            },
                            {
                                'address': '''3124 Espinoza Coves
Amystad, TX 30579''',
                                'familySize': 6,
                                'headOfHousehold': None,
                                'householdCaId': 'ead2e573-f9fb-4072-a309-14ffaf183830',
                                'location': {
                                    'title': 'East John'
                                },
                                'registrationDataImportId': {
                                    'name': 'Cost or than point.'
                                }
                            },
                            {
                                'address': '''8131 Kevin Highway Suite 059
Williamsport, MN 90545''',
                                'familySize': 6,
                                'headOfHousehold': None,
                                'householdCaId': 'efbec379-0e30-4619-8f9a-13a34147eb54',
                                'location': {
                                    'title': 'Catherinefort'
                                },
                                'registrationDataImportId': {
                                    'name': 'Nice sense yes law behavior seek.'
                                }
                            },
                            {
                                'address': '''0753 Cassie Ford Suite 067
Lake Matthewview, MD 19254''',
                                'familySize': 8,
                                'headOfHousehold': None,
                                'householdCaId': '872534c7-ac8a-43e1-9d0a-65b08b1b7290',
                                'location': {
                                    'title': 'Bradleyfort'
                                },
                                'registrationDataImportId': {
                                    'name': 'Republican despite model approach.'
                                }
                            }
                        ],
                        'lastEditedAt': '2020-03-03T18:04:20.714288',
                        'name': 'target_1',
                        'status': 'IN_PROGRESS'
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-03-03T18:04:20.715304',
                        'createdBy': {
                            'firstName': 'Erik',
                            'lastName': 'Clayton'
                        },
                        'households': [
                            {
                                'address': '''4272 Mark Corner Apt. 467
Haydenville, OH 07388''',
                                'familySize': 7,
                                'headOfHousehold': None,
                                'householdCaId': '68ebca0a-8210-4e5d-8a76-8591502a3a14',
                                'location': {
                                    'title': 'East Vanessa'
                                },
                                'registrationDataImportId': {
                                    'name': 'Home seat central tax.'
                                }
                            },
                            {
                                'address': '''933 Kim Ridges Apt. 258
Nicholasberg, DE 44958''',
                                'familySize': 8,
                                'headOfHousehold': None,
                                'householdCaId': 'a8c8fc5c-c931-402a-a85e-e1e5ef27acb1',
                                'location': {
                                    'title': 'Lake Franktown'
                                },
                                'registrationDataImportId': {
                                    'name': 'Into bit nation senior value feeling.'
                                }
                            },
                            {
                                'address': '''3124 Espinoza Coves
Amystad, TX 30579''',
                                'familySize': 6,
                                'headOfHousehold': None,
                                'householdCaId': 'ead2e573-f9fb-4072-a309-14ffaf183830',
                                'location': {
                                    'title': 'East John'
                                },
                                'registrationDataImportId': {
                                    'name': 'Cost or than point.'
                                }
                            },
                            {
                                'address': '''8131 Kevin Highway Suite 059
Williamsport, MN 90545''',
                                'familySize': 6,
                                'headOfHousehold': None,
                                'householdCaId': 'efbec379-0e30-4619-8f9a-13a34147eb54',
                                'location': {
                                    'title': 'Catherinefort'
                                },
                                'registrationDataImportId': {
                                    'name': 'Nice sense yes law behavior seek.'
                                }
                            },
                            {
                                'address': '''0753 Cassie Ford Suite 067
Lake Matthewview, MD 19254''',
                                'familySize': 8,
                                'headOfHousehold': None,
                                'householdCaId': '872534c7-ac8a-43e1-9d0a-65b08b1b7290',
                                'location': {
                                    'title': 'Bradleyfort'
                                },
                                'registrationDataImportId': {
                                    'name': 'Republican despite model approach.'
                                }
                            }
                        ],
                        'lastEditedAt': '2020-03-03T18:04:20.723578',
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
            'createdAt': '2020-03-03T18:04:20.704217',
            'createdBy': {
                'firstName': 'Erik',
                'lastName': 'Clayton'
            },
            'households': [
                {
                    'address': '''4272 Mark Corner Apt. 467
Haydenville, OH 07388''',
                    'familySize': 7,
                    'headOfHousehold': None,
                    'householdCaId': '68ebca0a-8210-4e5d-8a76-8591502a3a14',
                    'location': {
                        'title': 'East Vanessa'
                    },
                    'registrationDataImportId': {
                        'name': 'Home seat central tax.'
                    }
                },
                {
                    'address': '''933 Kim Ridges Apt. 258
Nicholasberg, DE 44958''',
                    'familySize': 8,
                    'headOfHousehold': None,
                    'householdCaId': 'a8c8fc5c-c931-402a-a85e-e1e5ef27acb1',
                    'location': {
                        'title': 'Lake Franktown'
                    },
                    'registrationDataImportId': {
                        'name': 'Into bit nation senior value feeling.'
                    }
                },
                {
                    'address': '''3124 Espinoza Coves
Amystad, TX 30579''',
                    'familySize': 6,
                    'headOfHousehold': None,
                    'householdCaId': 'ead2e573-f9fb-4072-a309-14ffaf183830',
                    'location': {
                        'title': 'East John'
                    },
                    'registrationDataImportId': {
                        'name': 'Cost or than point.'
                    }
                },
                {
                    'address': '''8131 Kevin Highway Suite 059
Williamsport, MN 90545''',
                    'familySize': 6,
                    'headOfHousehold': None,
                    'householdCaId': 'efbec379-0e30-4619-8f9a-13a34147eb54',
                    'location': {
                        'title': 'Catherinefort'
                    },
                    'registrationDataImportId': {
                        'name': 'Nice sense yes law behavior seek.'
                    }
                },
                {
                    'address': '''0753 Cassie Ford Suite 067
Lake Matthewview, MD 19254''',
                    'familySize': 8,
                    'headOfHousehold': None,
                    'householdCaId': '872534c7-ac8a-43e1-9d0a-65b08b1b7290',
                    'location': {
                        'title': 'Bradleyfort'
                    },
                    'registrationDataImportId': {
                        'name': 'Republican despite model approach.'
                    }
                }
            ],
            'lastEditedAt': '2020-03-03T18:04:20.714288',
            'name': 'target_1',
            'status': 'IN_PROGRESS'
        }
    }
}
