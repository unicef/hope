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
                        'createdAt': '2020-03-09T21:16:38.286418',
                        'createdBy': {
                            'firstName': 'Amanda',
                            'lastName': 'Campbell'
                        },
                        'households': {
                            'edges': [
                                {
                                    'node': {
                                        'address': '''099 Richardson Ramp
North Sarah, ND 69005''',
                                        'familySize': 4,
                                        'headOfHousehold': None,
                                        'householdCaId': '541f4f21-a736-4d4c-9649-365c2bc7cee8',
                                        'location': {
                                            'title': 'New Kevinland'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Play natural left perform record.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''27082 Julie Courts Apt. 387
Amyshire, ME 28865''',
                                        'familySize': 6,
                                        'headOfHousehold': None,
                                        'householdCaId': '6284ed31-2839-4c74-aa2e-ac1662987a55',
                                        'location': {
                                            'title': 'West Michelleberg'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Past exactly state best government clearly stop herself.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''2779 Sara Parks
Lake Carol, IA 69498''',
                                        'familySize': 5,
                                        'headOfHousehold': None,
                                        'householdCaId': '38ed58b0-84d1-4d63-93f0-4298e6fa5718',
                                        'location': {
                                            'title': 'Henryburgh'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Whatever culture according resource three relate police.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''USNS Smith
FPO AE 44907''',
                                        'familySize': 7,
                                        'headOfHousehold': None,
                                        'householdCaId': '2c909160-8d8f-42a3-b7a2-ec83216aad64',
                                        'location': {
                                            'title': 'Velezfurt'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Interest idea hospital career.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''PSC 0401, Box 0957
APO AP 19689''',
                                        'familySize': 3,
                                        'headOfHousehold': None,
                                        'householdCaId': 'fe539143-670b-4da9-a77e-a4a12005797b',
                                        'location': {
                                            'title': 'Port Eric'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Brother quite along kind fill strong.'
                                        }
                                    }
                                }
                            ]
                        },
                        'lastEditedAt': '2020-03-09T21:16:38.294981',
                        'name': 'target_1',
                        'status': 'FINALIZED'
                    }
                },
                {
                    'node': {
                        'createdAt': '2020-03-09T21:16:38.296042',
                        'createdBy': {
                            'firstName': 'Amanda',
                            'lastName': 'Campbell'
                        },
                        'households': {
                            'edges': [
                                {
                                    'node': {
                                        'address': '''099 Richardson Ramp
North Sarah, ND 69005''',
                                        'familySize': 4,
                                        'headOfHousehold': None,
                                        'householdCaId': '541f4f21-a736-4d4c-9649-365c2bc7cee8',
                                        'location': {
                                            'title': 'New Kevinland'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Play natural left perform record.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''27082 Julie Courts Apt. 387
Amyshire, ME 28865''',
                                        'familySize': 6,
                                        'headOfHousehold': None,
                                        'householdCaId': '6284ed31-2839-4c74-aa2e-ac1662987a55',
                                        'location': {
                                            'title': 'West Michelleberg'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Past exactly state best government clearly stop herself.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''2779 Sara Parks
Lake Carol, IA 69498''',
                                        'familySize': 5,
                                        'headOfHousehold': None,
                                        'householdCaId': '38ed58b0-84d1-4d63-93f0-4298e6fa5718',
                                        'location': {
                                            'title': 'Henryburgh'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Whatever culture according resource three relate police.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''USNS Smith
FPO AE 44907''',
                                        'familySize': 7,
                                        'headOfHousehold': None,
                                        'householdCaId': '2c909160-8d8f-42a3-b7a2-ec83216aad64',
                                        'location': {
                                            'title': 'Velezfurt'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Interest idea hospital career.'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'address': '''PSC 0401, Box 0957
APO AP 19689''',
                                        'familySize': 3,
                                        'headOfHousehold': None,
                                        'householdCaId': 'fe539143-670b-4da9-a77e-a4a12005797b',
                                        'location': {
                                            'title': 'Port Eric'
                                        },
                                        'registrationDataImportId': {
                                            'name': 'Brother quite along kind fill strong.'
                                        }
                                    }
                                }
                            ]
                        },
                        'lastEditedAt': '2020-03-09T21:16:38.303335',
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
            'createdAt': '2020-03-09T21:16:38.286418',
            'createdBy': {
                'firstName': 'Amanda',
                'lastName': 'Campbell'
            },
            'households': {
                'edges': [
                    {
                        'node': {
                            'address': '''099 Richardson Ramp
North Sarah, ND 69005''',
                            'familySize': 4,
                            'headOfHousehold': None,
                            'householdCaId': '541f4f21-a736-4d4c-9649-365c2bc7cee8',
                            'location': {
                                'title': 'New Kevinland'
                            },
                            'registrationDataImportId': {
                                'name': 'Play natural left perform record.'
                            }
                        }
                    },
                    {
                        'node': {
                            'address': '''27082 Julie Courts Apt. 387
Amyshire, ME 28865''',
                            'familySize': 6,
                            'headOfHousehold': None,
                            'householdCaId': '6284ed31-2839-4c74-aa2e-ac1662987a55',
                            'location': {
                                'title': 'West Michelleberg'
                            },
                            'registrationDataImportId': {
                                'name': 'Past exactly state best government clearly stop herself.'
                            }
                        }
                    },
                    {
                        'node': {
                            'address': '''2779 Sara Parks
Lake Carol, IA 69498''',
                            'familySize': 5,
                            'headOfHousehold': None,
                            'householdCaId': '38ed58b0-84d1-4d63-93f0-4298e6fa5718',
                            'location': {
                                'title': 'Henryburgh'
                            },
                            'registrationDataImportId': {
                                'name': 'Whatever culture according resource three relate police.'
                            }
                        }
                    },
                    {
                        'node': {
                            'address': '''USNS Smith
FPO AE 44907''',
                            'familySize': 7,
                            'headOfHousehold': None,
                            'householdCaId': '2c909160-8d8f-42a3-b7a2-ec83216aad64',
                            'location': {
                                'title': 'Velezfurt'
                            },
                            'registrationDataImportId': {
                                'name': 'Interest idea hospital career.'
                            }
                        }
                    },
                    {
                        'node': {
                            'address': '''PSC 0401, Box 0957
APO AP 19689''',
                            'familySize': 3,
                            'headOfHousehold': None,
                            'householdCaId': 'fe539143-670b-4da9-a77e-a4a12005797b',
                            'location': {
                                'title': 'Port Eric'
                            },
                            'registrationDataImportId': {
                                'name': 'Brother quite along kind fill strong.'
                            }
                        }
                    }
                ]
            },
            'lastEditedAt': '2020-03-09T21:16:38.294981',
            'name': 'target_1',
            'status': 'FINALIZED'
        }
    }
}
