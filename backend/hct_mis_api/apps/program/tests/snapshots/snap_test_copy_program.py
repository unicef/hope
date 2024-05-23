# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCopyProgram::test_copy_program_incompatible_collecting_type 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': "['The Data Collection Type must be compatible with the original Programme.']",
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_not_authenticated 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User is not authenticated.',
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_with_existing_name 1'] = {
    'data': {
        'copyProgram': {
            'program': None,
            'validationErrors': {
                '__all__': [
                    'Program for name: initial name and business_area: afghanistan already exists.'
                ]
            }
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_with_partners_0_valid 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'SELECTED_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    },
                    {
                        'areaAccess': 'ADMIN_AREA',
                        'areas': [
                            {
                                'name': 'North Brianmouth'
                            },
                            {
                                'name': 'South Catherine'
                            }
                        ],
                        'name': 'WFP'
                    },
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'New Partner'
                    }
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_with_partners_1_invalid_all_partner_access 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'You cannot specify partners for the chosen access type',
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_with_partners_2_invalid_none_partner_access 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'You cannot specify partners for the chosen access type',
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_program_with_partners_all_partners_access 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'ALL_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    },
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'Other Partner'
                    }
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_with_partners_none_partners_access 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'NONE_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    }
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}

snapshots['TestCopyProgram::test_copy_program_without_permissions 1'] = {
    'data': {
        'copyProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'copyProgram'
            ]
        }
    ]
}

snapshots['TestCopyProgram::test_copy_with_permissions 1'] = {
    'data': {
        'copyProgram': {
            'program': {
                'administrativeAreasOfImplementation': 'Lorem Ipsum',
                'budget': '20000000.00',
                'cashPlus': True,
                'description': 'my description of program',
                'endDate': '2021-12-20',
                'frequencyOfPayments': 'REGULAR',
                'name': 'copied name',
                'partnerAccess': 'NONE_PARTNERS_ACCESS',
                'partners': [
                    {
                        'areaAccess': 'BUSINESS_AREA',
                        'areas': [
                            {
                                'name': 'Area in AFG 1'
                            },
                            {
                                'name': 'Area in AFG 2'
                            }
                        ],
                        'name': 'UNICEF'
                    }
                ],
                'populationGoal': 150000,
                'sector': 'EDUCATION',
                'startDate': '2019-12-20'
            },
            'validationErrors': None
        }
    }
}
