# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

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
                        'birthDate': '1978-01-02',
                        'familyName': 'Parker',
                        'fullName': 'Peter Parker',
                        'givenName': 'Peter',
                        'phoneNo': '(666)682-2345',
                        'phoneNoValid': False
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
                        'birthDate': '1965-06-26',
                        'familyName': 'Bond',
                        'fullName': 'James Bond',
                        'givenName': 'James',
                        'phoneNo': '(007)682-4596',
                        'phoneNoValid': False
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

snapshots['TestIndividualQuery::test_individual_query_all_for_all_programs 1'] = {
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
                        'birthDate': '1978-01-02',
                        'familyName': 'Parker',
                        'fullName': 'Peter Parker',
                        'givenName': 'Peter',
                        'phoneNo': '(666)682-2345',
                        'phoneNoValid': False
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
                        'birthDate': '1965-06-26',
                        'familyName': 'Bond',
                        'fullName': 'James Bond',
                        'givenName': 'James',
                        'phoneNo': '(007)682-4596',
                        'phoneNoValid': False
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

snapshots['TestIndividualQuery::test_individual_query_all_for_all_programs_user_with_no_program_access 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_individual_query_draft 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
            ]
        }
    }
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

snapshots['TestIndividualQuery::test_individual_query_single_different_program_in_header 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_admin2_0_with_permission 1'] = {
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
                        'birthDate': '1978-01-02',
                        'familyName': 'Parker',
                        'fullName': 'Peter Parker',
                        'givenName': 'Peter',
                        'phoneNo': '(666)682-2345',
                        'phoneNoValid': False
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
                        'birthDate': '1965-06-26',
                        'familyName': 'Bond',
                        'fullName': 'James Bond',
                        'givenName': 'James',
                        'phoneNo': '(007)682-4596',
                        'phoneNoValid': False
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

snapshots['TestIndividualQuery::test_query_individuals_by_admin2_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_bank_account_number_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1965-06-26',
                        'familyName': 'Bond',
                        'fullName': 'James Bond',
                        'givenName': 'James',
                        'phoneNo': '(007)682-4596',
                        'phoneNoValid': False
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_query_individuals_by_search_bank_account_number_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_birth_certificate_filter_0_with_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_birth_certificate_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_disability_card_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1978-01-02',
                        'familyName': 'Parker',
                        'fullName': 'Peter Parker',
                        'givenName': 'Peter',
                        'phoneNo': '(666)682-2345',
                        'phoneNoValid': False
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_query_individuals_by_search_disability_card_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_drivers_license_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_drivers_license_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_full_name_filter_0_with_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_full_name_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_national_id_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_national_id_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_national_passport_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1946-02-15',
                        'familyName': 'Ford',
                        'fullName': 'Robin Ford',
                        'givenName': 'Robin',
                        'phoneNo': '+18663567905',
                        'phoneNoValid': True
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_query_individuals_by_search_national_passport_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_phone_no_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_phone_no_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_detail_id_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_detail_id_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_detail_id_filter_with_search_type_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_detail_id_filter_with_search_type_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_tax_id_filter_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1983-12-21',
                        'familyName': 'Perry',
                        'fullName': 'Timothy Perry',
                        'givenName': 'Timothy',
                        'phoneNo': '(548)313-1700-902',
                        'phoneNoValid': False
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_query_individuals_by_search_tax_id_filter_1_without_permission 1'] = {
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

snapshots['TestIndividualQuery::test_query_individuals_by_search_without_search_type_0_with_permission 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_query_individuals_by_search_without_search_type_1_without_permission 1'] = {
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

snapshots['TestIndividualWithDeliveryMechanismsDataQuery::test_individual_query_accounts_0_with_permissions 1'] = {
    'data': {
        'individual': {
            'birthDate': '1943-07-30',
            'accounts': [
                {
                    'individualTabData': '{"card_expiry_date": "2022-01-01", "card_number": "123", "name_of_cardholder": "Marek", "number": "123", "financial_institution": "2"}',
                    'name': 'Bank'
                },
                {
                    'individualTabData': '{"delivery_phone_number": "123456789", "provider": "Provider", "service_provider_code": "ABC", "number": "321", "financial_institution": "2"}',
                    'name': 'Mobile'
                }
            ],
            'familyName': 'Butler',
            'fullName': 'Benjamin Butler',
            'givenName': 'Benjamin',
            'phoneNo': '(953)682-4596'
        }
    }
}

snapshots['TestIndividualWithDeliveryMechanismsDataQuery::test_individual_query_accounts_1_without_permissions 1'] = {
    'data': {
        'individual': {
            'birthDate': '1943-07-30',
            'accounts': [
            ],
            'familyName': 'Butler',
            'fullName': 'Benjamin Butler',
            'givenName': 'Benjamin',
            'phoneNo': '(953)682-4596'
            ''
        }
    }
}

snapshots['TestIndividualWithFlexFieldsQuery::test_individual_query_single_with_flex_fields 1'] = {
    'data': {
        'individual': {
            'birthDate': '1943-07-30',
            'familyName': 'Butler',
            'flexFields': {
                'pdu_field_1': {
                    '1': {
                        'collection_date': '2021-01-01',
                        'value': 123.45
                    },
                    '2': {
                        'collection_date': '2021-01-01',
                        'value': 234.56
                    }
                },
                'pdu_field_2': {
                    '4': {
                        'collection_date': '2021-01-01',
                        'value': 'Value D'
                    }
                }
            },
            'fullName': 'Benjamin Butler',
            'givenName': 'Benjamin',
            'phoneNo': '(953)682-4596'
        }
    }
}
