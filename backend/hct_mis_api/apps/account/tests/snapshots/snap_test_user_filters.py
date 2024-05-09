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
                            'name': 'Test Partner with Program Access'
                        },
                        'partnerRoles': [
                        ],
                        'userRoles': [
                            {
                                'businessArea': {
                                    'name': 'Afghanistan'
                                },
                                'role': {
                                    'name': 'User Management View Role',
                                    'permissions': [
                                        'USER_MANAGEMENT_VIEW_LIST'
                                    ]
                                }
                            }
                        ],
                        'username': 'user_with_role_in_BA'
                    }
                },
                {
                    'node': {
                        'partner': {
                            'name': 'Default Empty Partner'
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
                            'name': 'Test Partner with Program Access'
                        },
                        'username': 'user_with_role_in_BA'
                    }
                },
                {
                    'node': {
                        'partner': {
                            'name': 'Partner With Test Role'
                        },
                        'username': 'user_with_partner_with_test_role'
                    }
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
                            'name': 'Default Empty Partner'
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
