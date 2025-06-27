# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestUserFilter::test_users_by_business_area 1'] = {
    'data': {
        'allUsers': {
            'edges': [
                {
                    'node': {
                        'partner': {
                            'name': 'UNICEF'
                        },
                        'partnerRoles': [
                        ],
                        'userRoles': [
                            {
                                'businessArea': {
                                    'name': 'Afghanistan'
                                },
                                'role': {
                                    'name': 'Test Role',
                                    'permissions': None
                                }
                            }
                        ],
                        'username': 'user_with_test_role'
                    }
                },
                {
                    'node': {
                        'partner': {
                            'name': 'Partner With Test Role'
                        },
                        'partnerRoles': [
                            {
                                'businessArea': {
                                    'name': 'Afghanistan'
                                },
                                'roles': [
                                    {
                                        'name': 'Test Role',
                                        'permissions': None
                                    },
                                    {
                                        'name': 'User Management View Role',
                                        'permissions': [
                                            'USER_MANAGEMENT_VIEW_LIST'
                                        ]
                                    }
                                ]
                            }
                        ],
                        'userRoles': [
                        ],
                        'username': 'user_with_partner_with_test_role'
                    }
                }
            ]
        }
    }
}

snapshots['TestUserFilter::test_users_by_program 1'] = {
    'data': {
        'allUsers': {
            'edges': [
                {
                    'node': {
                        'partner': {
                            'name': 'UNICEF'
                        },
                        'username': 'user_with_test_role'
                    }
                },
                {
                    'node': {
                        'partner': {
                            'name': 'Partner With Test Role'
                        },
                        'username': 'user_with_partner_with_test_role'
                    },
                }
            ]
        }
    }
}

snapshots['TestUserFilter::test_users_by_roles 1'] = {
    'data': {
        'allUsers': {
            'edges': [
                {
                    'node': {
                        'partner': {
                            'name': 'UNICEF'
                        },
                        'partnerRoles': [
                        ],
                        'userRoles': [
                            {
                                'businessArea': {
                                    'name': 'Afghanistan'
                                },
                                'role': {
                                    'name': 'Test Role',
                                    'permissions': None
                                }
                            }
                        ],
                        'username': 'user_with_test_role'
                    }
                },
                {
                    'node': {
                        'partner': {
                            'name': 'Partner With Test Role'
                        },
                        'partnerRoles': [
                            {
                                'businessArea': {
                                    'name': 'Afghanistan'
                                },
                                'roles': [
                                    {
                                        'name': 'Test Role',
                                        'permissions': None
                                    },
                                    {
                                        'name': 'User Management View Role',
                                        'permissions': [
                                            'USER_MANAGEMENT_VIEW_LIST'
                                        ]
                                    }
                                ]
                            }
                        ],
                        'userRoles': [
                        ],
                        'username': 'user_with_partner_with_test_role'
                    }
                }
            ]
        }
    }
}
