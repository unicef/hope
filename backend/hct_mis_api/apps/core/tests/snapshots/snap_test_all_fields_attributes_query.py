# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestMetaDataFilterType::test_core_meta_type_query 1'] = {
    'data': {
        'allFieldsAttributes': [
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': 'Count the number of locally-made or imported ploughing tools.'}",
                'isFlexField': True,
                'labelEn': 'Number of ploughing tools.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of ploughing tools.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'Agric_tool_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '{\'English(EN)\': "Put \'-1\', if there is no child. Take the youngest children of school going age. 0.5 for each upper piece of clothing and 0.5 for each lower piece of clothing"}',
                'isFlexField': True,
                'labelEn': "Number of complete children's clothes.",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': "Number of complete children's clothes.",
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'Child_clothes_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': 'Count the number of 5 litre or more saucepans as 1 piece.'}",
                'isFlexField': True,
                'labelEn': 'Number of Cooking pots.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of Cooking pots.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'Cooking_pot_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Food consumption score',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Food consumption score',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'FCS_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '{\'English(EN)\': "Put \'-1\', if no women is present 1 complete set = 0.5 up ( eg Blouse/t-shirt)and 0.5 down (loincloths/skirts).The clothes of the mother or main woman in the household AND those of the oldest school aged girls in the house should be counted"}',
                'isFlexField': True,
                'labelEn': "Number of complete women's clothes.",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': "Number of complete women's clothes.",
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'Women_clothes_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': '0p. At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '0p. At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': '1p. Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '1p. Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    },
                    {
                        'labelEn': '2p. Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '2p. Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2.0'
                    },
                    {
                        'labelEn': '3p More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '3p More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3.0'
                    },
                    {
                        'labelEn': '4p. Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '4p. Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4.0'
                    },
                    {
                        'labelEn': '5p. All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '5p. All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '3. I have felt active and vigorous',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '3. I have felt active and vigorous',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'active_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Did your family receive any type of assistance in the past six months?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Did your family receive any type of assistance in the past six months?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'assistance_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': "Don't know",
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': "Don't know",
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'dont_know_source'
                    },
                    {
                        'labelEn': 'Governmental',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Governmental',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'governmental'
                    },
                    {
                        'labelEn': 'NGOs, religious organizations and CBOs',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'NGOs, religious organizations and CBOs',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'ngos'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'other'
                    },
                    {
                        'labelEn': 'Other INGO (non UN related)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other INGO (non UN related)',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'other_ingo'
                    },
                    {
                        'labelEn': 'Relatives/friends/neighbors',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Relatives/friends/neighbors',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'relatives_friends'
                    },
                    {
                        'labelEn': 'UNHCR',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'UNHCR',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'unhcr'
                    },
                    {
                        'labelEn': 'UNICEF',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'UNICEF',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'unicef'
                    },
                    {
                        'labelEn': 'WFP',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'WFP',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'wfp'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Did your family get assistance from any of these sources in the last 6 months?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Did your family get assistance from any of these sources in the last 6 months?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'assistance_source_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Cash assistance',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Cash assistance',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'cash_assistance'
                    },
                    {
                        'labelEn': 'Child cash grant',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child cash grant',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'child_cash_grant'
                    },
                    {
                        'labelEn': 'Child education grant',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child education grant',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'child_edu_grant'
                    },
                    {
                        'labelEn': "Don't Know",
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': "Don't Know",
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'don’t_know'
                    },
                    {
                        'labelEn': 'Food assistance for children',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Food assistance for children',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'food_for_children'
                    },
                    {
                        'labelEn': 'Food assistance in-kind support',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Food assistance in-kind support',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'food_in_kind'
                    },
                    {
                        'labelEn': 'Food assistance vouchers',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Food assistance vouchers',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'food_vouchers'
                    },
                    {
                        'labelEn': 'Health medical services',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Health medical services',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'health_services'
                    },
                    {
                        'labelEn': 'Informal education',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Informal education',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'informal_education'
                    },
                    {
                        'labelEn': 'Job opportunities',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Job opportunities',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'job_opportunities'
                    },
                    {
                        'labelEn': 'None of the above',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'None of the above',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'none_of_listed'
                    },
                    {
                        'labelEn': 'Psychosocial services',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Psychosocial services',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'psychosocial'
                    },
                    {
                        'labelEn': 'School feeding',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'School feeding',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'school_feeding'
                    },
                    {
                        'labelEn': 'School material',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'School material',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'school_material'
                    },
                    {
                        'labelEn': 'Training',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Training',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'training'
                    },
                    {
                        'labelEn': 'Voucher',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Voucher',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'voucher'
                    },
                    {
                        'labelEn': 'Winterization assistance',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Winterization assistance',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'winterization'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What type of assistance did your family receive in the past six months?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What type of assistance did your family receive in the past six months?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'assistance_type_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the average daily income of the child',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the average daily income of the child',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'avg_child_dailyincome_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the Family’s average daily income in ${currency_h_c}',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the Family’s average daily income in ${currency_h_c}',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'avg_hhdaily_income_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': 'Count only the number of 10 or more litre bowls as a unit, if a bowl is dammaged, count 0.5.'}",
                'isFlexField': True,
                'labelEn': 'Number of Bassins',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of Bassins',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'bassin_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': '1 bedding facility of 1 place (01 person) = 1 piece; 1 support of 2 places = 2 pieces.'}",
                'isFlexField': True,
                'labelEn': 'Number of bedding facilities (beds, mats, mattresses,…)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of bedding facilities (beds, mats, mattresses,…)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'beds_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'I believe my children will have a better life.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'I believe my children will have a better life.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'believe_better_life_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': 'If the sheets are in bad state but still usable, count 0.5 (1/2) a piece.'}",
                'isFlexField': True,
                'labelEn': 'Number of blankets/sheets.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of blankets/sheets.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'blanket_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If there is any children <1 year, is he/she being breastfed?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If there is any children <1 year, is he/she being breastfed?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'breastfed_child_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Cereals & grains: e.g maize meal, rice, pasta, bread, bulgur, …',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Cereals & grains: e.g maize meal, rice, pasta, bread, bulgur, …',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'cereals_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Cereals & grains: e.g maize meal, rice, pasta, bread, bulgur, …',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Cereals & grains: e.g maize meal, rice, pasta, bread, bulgur, …',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'cereals_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Cereals & grains + tubers & roots score',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Cereals & grains + tubers & roots score',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'cereals_tuber_score_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': '0p. At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '0p. At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': '1p. Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '1p. Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    },
                    {
                        'labelEn': '2p. Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '2p. Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2.0'
                    },
                    {
                        'labelEn': '3p More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '3p More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3.0'
                    },
                    {
                        'labelEn': '4p. Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '4p. Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4.0'
                    },
                    {
                        'labelEn': '5p. All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '5p. All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '1. I have felt cheerful and in good spirits',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '1. I have felt cheerful and in good spirits',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'cheer_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Is the child out of school engaged in work?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Is the child out of school engaged in work?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'child_engaged_work_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What type of work is the child engaged in?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What type of work is the child engaged in?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'child_engaged_worktype_i_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If someone hurts my child or something bad happens to them, it is not their fault.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If someone hurts my child or something bad happens to them, it is not their fault.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'child_not_at_fault_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'home',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'home',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'home'
                    },
                    {
                        'labelEn': 'other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'other'
                    },
                    {
                        'labelEn': 'street',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'street',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'street'
                    },
                    {
                        'labelEn': 'work place',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'work place',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'work_place'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Where does the child spend his/her night:',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Where does the child spend his/her night:',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'child_where_night_i_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'I believe my children are safe in the area that we live.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'I believe my children are safe in the area that we live.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'children_safe_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Clothing including shoes for adults',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Clothing including shoes for adults',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'clothing_adult_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Clothing including shoes for children',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Clothing including shoes for children',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'clothing_child_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Bought food on credit or borrowed money to purchase food',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Bought food on credit or borrowed money to purchase food',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'borrowed_money'
                    },
                    {
                        'labelEn': 'Changed accommodation location or type in order to reduce rental expenditure',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Changed accommodation location or type in order to reduce rental expenditure',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'changed_location'
                    },
                    {
                        'labelEn': 'Child marriage',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child marriage',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'child_marriage'
                    },
                    {
                        'labelEn': 'Adult members of the household accepted socially degrading, exploitative, high risk or illegal temporary jobs',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult members of the household accepted socially degrading, exploitative, high risk or illegal temporary jobs',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'illegal_jobs'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'other'
                    },
                    {
                        'labelEn': 'Reduced essential non food expenditure such as education/health',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Reduced essential non food expenditure such as education/health',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'reduced_essential'
                    },
                    {
                        'labelEn': 'Sell productive assets or means of transport (sewing machine, car, wheel barrow, bicycle, motorbike, etc)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sell productive assets or means of transport (sewing machine, car, wheel barrow, bicycle, motorbike, etc)',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'sell_assets'
                    },
                    {
                        'labelEn': 'Sell household goods (jewelry, phone, furniture, electro domestics, etc)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sell household goods (jewelry, phone, furniture, electro domestics, etc)',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'sell_hh_goods'
                    },
                    {
                        'labelEn': 'Sent adult family members to beg',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sent adult family members to beg',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'sent_adult_beg'
                    },
                    {
                        'labelEn': 'Sent children (under 18) family members to beg',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sent children (under 18) family members to beg',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'sent_child_beg'
                    },
                    {
                        'labelEn': 'Spent savings',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Spent savings',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'spent_savings'
                    },
                    {
                        'labelEn': 'Withdrawn children from school',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Withdrawn children from school',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'withdrawn_child'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'In the past 30 days, has your family applied any of the below strategies to meet food and basic needs?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'In the past 30 days, has your family applied any of the below strategies to meet food and basic needs?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategies_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If “Mortgaged”, how much rent is paid each month in ${currency_h_c}?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If “Mortgaged”, how much rent is paid each month in ${currency_h_c}?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'cost_mortgage_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If “Rented”, how much rent is paid each month in ${currency_h_c}?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If “Rented”, how much rent is paid each month in ${currency_h_c}?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'cost_rent_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Milk and dairy products: yoghurt, cheese',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Milk and dairy products: yoghurt, cheese',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'dairy_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Milk and dairy products: yoghurt, cheese',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Milk and dairy products: yoghurt, cheese',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'dairy_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How many days did your household not have water for household needs in the past month?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many days did your household not have water for household needs in the past month?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'days_no_water_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Number of days out of school engaged work?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of days out of school engaged work?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'days_out_of_school_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Debt repayments',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Debt repayments',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'debt_repay_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Annually',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Annually',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'annually_desludge'
                    },
                    {
                        'labelEn': 'Monthly',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Monthly',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'monthly_desludge'
                    },
                    {
                        'labelEn': 'Quarterly',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Quarterly',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'quarterly_desludge'
                    },
                    {
                        'labelEn': 'Weekly',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Weekly',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'weekly_desludge'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How often do you have to desludge your septic tank?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How often do you have to desludge your septic tank?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'desludge_tank_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Bullying among students',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Bullying among students',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'bullying'
                    },
                    {
                        'labelEn': 'Distance to school',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Distance to school',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'distance_school'
                    },
                    {
                        'labelEn': 'Not inclusive for children with disabilities',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not inclusive for children with disabilities',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'exclude_disabled'
                    },
                    {
                        'labelEn': 'Financial constraints',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Financial constraints',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'financial_cons'
                    },
                    {
                        'labelEn': 'No interest in learning',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No interest in learning',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'no_interest'
                    },
                    {
                        'labelEn': 'Performance issues',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Performance issues',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'performance_issues'
                    },
                    {
                        'labelEn': 'Physical abuse from staff',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Physical abuse from staff',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'physical_abuse'
                    },
                    {
                        'labelEn': 'Poor quality of teaching and/or management (service)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Poor quality of teaching and/or management (service)',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'poor_teaching'
                    },
                    {
                        'labelEn': 'Psycological distress / severely distressed',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Psycological distress / severely distressed',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'psych_distress'
                    },
                    {
                        'labelEn': 'Safety fears for movement outside home',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Safety fears for movement outside home',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'safety_fear'
                    },
                    {
                        'labelEn': 'Humiliation, discrimination, verbal abuse from staff',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Humiliation, discrimination, verbal abuse from staff',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'verbal_abuse'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What difficulties or challenges is he/she experiencing?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What difficulties or challenges is he/she experiencing?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'diff_challenges_i_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If any child was sick, When he/she had an illness with a cough, did he/she breathe faster than usual with short, rapid breaths or have difficulty breathing?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If any child was sick, When he/she had an illness with a cough, did he/she breathe faster than usual with short, rapid breaths or have difficulty breathing?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'difficulty_breathing_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How many liters of water could your family access yesterday? (calculated):   ${total_liter_yesterday_h_f}',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many liters of water could your family access yesterday? (calculated):   ${total_liter_yesterday_h_f}',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'display_total_liter_h_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How many minutes does it take for members of your household to go there, get water, and come back?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many minutes does it take for members of your household to go there, get water, and come back?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'distace_to_water_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Does your latrine have door, light, ventilation?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Does your latrine have door, light, ventilation?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'door_light_vent_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Buy water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Buy water',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'buy_water'
                    },
                    {
                        'labelEn': 'Collector',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Collector',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'collect_water'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Do you buy or collect from this source?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Do you buy or collect from this source?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'drinking_water_acquire_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Packaged water (bottled water, sachets_',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Packaged water (bottled water, sachets_',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'packaged_water'
                    },
                    {
                        'labelEn': 'Piped water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Piped water',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'piped_water'
                    },
                    {
                        'labelEn': 'From private vendor',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'From private vendor',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'private_vendor_water'
                    },
                    {
                        'labelEn': 'Rain water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rain water',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'rain_water'
                    },
                    {
                        'labelEn': 'Spring water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Spring water',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'spring_water'
                    },
                    {
                        'labelEn': 'Surface water (river, dam, lake, pond, canal, irrigation channel)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Surface water (river, dam, lake, pond, canal, irrigation channel)',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'surface_water'
                    },
                    {
                        'labelEn': 'Water tank',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Water tank',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'water_tank'
                    },
                    {
                        'labelEn': 'Water from a well',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Water from a well',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'well_water'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is your primary source of drinking water?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is your primary source of drinking water?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'drinking_water_source_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Brother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Brother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'brother'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'mother'
                    },
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'no'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'other'
                    },
                    {
                        'labelEn': 'Sister',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sister',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'sister'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Is there any drug addict in the family?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Is there any drug addict in the family?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'drug_addict_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Education (books, uniform, stationary, fees)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Education (books, uniform, stationary, fees)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'education_fees_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Eggs',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Eggs',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'eggs_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Fish and other seafood',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Fish and other seafood',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'fish_hhds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If your child is attending a school, does he/she experience challenges?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If your child is attending a school, does he/she experience challenges?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'formal_school_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': '0p. At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '0p. At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': '1p. Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '1p. Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    },
                    {
                        'labelEn': '2p. Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '2p. Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2.0'
                    },
                    {
                        'labelEn': '3p More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '3p More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3.0'
                    },
                    {
                        'labelEn': '4p. Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '4p. Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4.0'
                    },
                    {
                        'labelEn': '5p. All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '5p. All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '4. I woke up feeling fresh and rested',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '4. I woke up feeling fresh and rested',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'fresh_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Fruits: e.g citrus, apple, banana, dates, …',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Fruits: e.g citrus, apple, banana, dates, …',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'fruits_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Fruits: e.g citrus, apple, banana, dates, …',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Fruits: e.g citrus, apple, banana, dates, …',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'fruits_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (micro-credit):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (micro-credit):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_credit_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': "Generated by (service job in someone else's house):",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': "Generated by (service job in someone else's house):",
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_domestic_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (end of service payment):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (end of service payment):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_endpmt_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (household enterprise):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (household enterprise):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_enterprise_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (gift from family):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (gift from family):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_gift_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (cash transfer from government):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (cash transfer from government):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_gov_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (paid job):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (paid job):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_job_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by( loan - bank, financial institution):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by( loan - bank, financial institution):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_loanbank_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (loan- family, friend):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (loan- family, friend):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_loanfamily_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (cash transfer from NGO, CBO, religious org.):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (cash transfer from NGO, CBO, religious org.):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_ngo_cbo_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (other income source):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (other income source):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_other_inc_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (remittance from family):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (remittance from family):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_remit_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (rental property):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (rental property):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_rent_profit_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (sale of assets):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (sale of assets):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_sale_asset_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (self-employment):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (self-employment):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_self_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (selling agricultural production):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (selling agricultural production):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_sellagricult_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (UNHCR cash transfer):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (UNHCR cash transfer):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_unhcr_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (UNICEF child cash grant):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (UNICEF child cash grant):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_unicef_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Adult',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Adult',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_adult'
                    },
                    {
                        'labelEn': 'Child',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_child'
                    },
                    {
                        'labelEn': 'Father',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Father',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_father'
                    },
                    {
                        'labelEn': 'Mother',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Mother',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_mother'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'by_other'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Generated by (WFP assistance):',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Generated by (WFP assistance):',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'gen_wfp_assist_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Household Dietary Diversity Score',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Household Dietary Diversity Score',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'hdds_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Other Health related expenditures (not for children)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Other Health related expenditures (not for children)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'health_adult_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Basic Hygiene items (soap, shampoo, toothpaste, sanitary pads, diapers)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Basic Hygiene items (soap, shampoo, toothpaste, sanitary pads, diapers)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'hygiene_items_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Hand washing facilities',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Hand washing facilities',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'hand_washing'
                    },
                    {
                        'labelEn': 'Soap',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Soap',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'soap_material'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What hygiene materials are available for the family?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What hygiene materials are available for the family?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'hygiene_materials_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '17. Sale of assets (including livestock, land)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '17. Sale of assets (including livestock, land)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_asset_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '9. Micro-credit',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '9. Micro-credit',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_credit_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '3. Domestic service job in someone else’s house',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '3. Domestic service job in someone else’s house',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_domestic_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '6. End of service payment',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '6. End of service payment',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_endpmt_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '18. Income (or goods) from household enterprise (profit or otherwise)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '18. Income (or goods) from household enterprise (profit or otherwise)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_enterprise_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '8. Gift from family/friend/other person',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '8. Gift from family/friend/other person',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_gift_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '14. Cash transfer from government',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '14. Cash transfer from government',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_gov_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '1. Paid job with an organization/businesses (salaries, wages, bonuses, allowances, commissions, gratuities)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '1. Paid job with an organization/businesses (salaries, wages, bonuses, allowances, commissions, gratuities)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_job_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '16. Loan (bank, other financial institution or organization)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '16. Loan (bank, other financial institution or organization)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_loanbank_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '15. Loan (family, friend)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '15. Loan (family, friend)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_loanfamily_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '13. Cash transfer from an NGO, CBOs , or religious organization',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '13. Cash transfer from an NGO, CBOs , or religious organization',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_ngo_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '19. Any other source?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '19. Any other source?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_other_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '7. Remittances from family (abroad or employed elsewhere)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '7. Remittances from family (abroad or employed elsewhere)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_remit_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '2. Profit from rental property you own',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '2. Profit from rental property you own',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_rental_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '4. Payment for self-employment (selling or making things, doing repairs, providing service, etc.)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '4. Payment for self-employment (selling or making things, doing repairs, providing service, etc.)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_self_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '5. Selling of your own agricultural production',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '5. Selling of your own agricultural production',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_sellagricult_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '11. UNHCR cash transfer',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '11. UNHCR cash transfer',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_unhcr_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '10. UNICEF child cash grant',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '10. UNICEF child cash grant',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_unicef_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '12. WFP assistance',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '12. WFP assistance',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'inc_wfp_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Infant needs (infant food)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Infant needs (infant food)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'infant_food_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': '0p. At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '0p. At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': '1p. Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '1p. Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    },
                    {
                        'labelEn': '2p. Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '2p. Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2.0'
                    },
                    {
                        'labelEn': '3p More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '3p More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3.0'
                    },
                    {
                        'labelEn': '4p. Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '4p. Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4.0'
                    },
                    {
                        'labelEn': '5p. All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '5p. All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '5. My daily life has been filled with things that interest me',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '5. My daily life has been filled with things that interest me',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'interested_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Income generating activity investment',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Income generating activity investment',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'investment_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': 'Count only the number (capacity) of 5 or more litre cans, if a can is dammaged, count it as half its volume.'}",
                'isFlexField': True,
                'labelEn': 'Total capacity of jerrycans (in litres)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Total capacity of jerrycans (in litres)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'jerrycans_capacity_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'I know where to go if my child needs access to a service.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'I know where to go if my child needs access to a service.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'know_access_service_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Pit',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Pit',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'pit_connection'
                    },
                    {
                        'labelEn': 'Public sewer',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Public sewer',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'public_sewer'
                    },
                    {
                        'labelEn': 'Septic tank',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Septic tank',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'septic_tank'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Is your household latrine connected to any of the following?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Is your household latrine connected to any of the following?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'latrine_connect_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'It is against the Law for children under the age of 16 to work.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'It is against the Law for children under the age of 16 to work.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'law_against_underage_work_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If the family needs it, children should leave school to work.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If the family needs it, children should leave school to work.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'leave_school_to_work_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Level of debt in ${currency_h_c}',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Level of debt in ${currency_h_c}',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'level_debt_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Established camps (e.g refugee camp, POC site, …)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Established camps (e.g refugee camp, POC site, …)',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'camps'
                    },
                    {
                        'labelEn': 'Accommodation is free / other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Accommodation is free / other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'free_accomodation'
                    },
                    {
                        'labelEn': 'Informal settlement',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Informal settlement',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'informal settlement'
                    },
                    {
                        'labelEn': 'Own the place I live in',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Own the place I live in',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'own'
                    },
                    {
                        'labelEn': 'Rent the place I live in with a formal contract',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rent the place I live in with a formal contract',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'rent_formal_contract'
                    },
                    {
                        'labelEn': 'Rent the place I live in with an informal contract',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rent the place I live in with an informal contract',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'rent_informal_contract'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': "What is the household's living situation?",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': "What is the household's living situation?",
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'living_situation_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If child is married, age at the time of first marriage?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If child is married, age at the time of first marriage?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'marriage_age_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Yesterday, how many meals were eaten by your family?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Yesterday, how many meals were eaten by your family?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'meals_yesterday_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Meat, fish and eggs: Beef, lamb chicken, liver, kidney, fish including canned tuna, eggs',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Meat, fish and eggs: Beef, lamb chicken, liver, kidney, fish including canned tuna, eggs',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'meat_fish_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Meat: Beef, lamb chicken, liver, kidney, …',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Meat: Beef, lamb chicken, liver, kidney, …',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'meat_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'I can meet the needs of the children in my care.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'I can meet the needs of the children in my care.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'meet_child_needs_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How many minutes does it take for the child to go to the nearest available school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many minutes does it take for the child to go to the nearest available school?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'minutes_to_school_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Food',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Food',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'monthly_food_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Rent (monthly)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Rent (monthly)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'monthly_rent_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Utilities (fuel, gas, electricity, etc)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Utilities (fuel, gas, electricity, etc)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'monthly_utilities_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Length of time since arrival (in months)?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Length of time since arrival (in months)?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'months_displaced_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the child Mid-upper arm circumference (MUAC) in mm?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the child Mid-upper arm circumference (MUAC) in mm?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'muac_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Essential Household Items / Non Food Items (blankets, cooking tools)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Essential Household Items / Non Food Items (blankets, cooking tools)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'nonfood_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the number of rooms in the dwelling excluding kitchen & bathroom?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the number of rooms in the dwelling excluding kitchen & bathroom?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'number_of_rooms_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Number of times displaced',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of times displaced',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'number_times_displaced_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Do you have odor, taste color in the water?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Do you have odor, taste color in the water?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'odor_taste_color_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Oil / fat: vegetable oil, palm oil, butter, ghee',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Oil / fat: vegetable oil, palm oil, butter, ghee',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'oilfat_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Oil / fat: vegetable oil, palm oil, butter, ghee',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Oil / fat: vegetable oil, palm oil, butter, ghee',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'oilfat_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'It is okay when a child gets hit at home by his parents for misbehaving.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'It is okay when a child gets hit at home by his parents for misbehaving.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'ok_parent_hit_child_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'It is okay when a child gets hit at school by his teacher for misbehaving.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'It is okay when a child gets hit at school by his teacher for misbehaving.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'ok_teacher_hit_child_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If there is more than one bedroom, what is the highest number of individuals living in one room?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If there is more than one bedroom, what is the highest number of individuals living in one room?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'one_room_dwellers_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Specify other coping strategies',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Specify other coping strategies',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'other_coping_strategy_h_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Other expenses',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Other expenses',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'other_expense_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Specify other income source:',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Specify other income source:',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'other_name_h_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If other, specify',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If other, specify',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'other_treatment_facility_h_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Are both mother and father of the child alive?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Are both mother and father of the child alive?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'parents_alive_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If one or both have passed away, what is the reason of their death',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If one or both have passed away, what is the reason of their death',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'parents_death_reason_i_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Pulses, nuts & seeds : beans, chickpeas, lentils',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Pulses, nuts & seeds : beans, chickpeas, lentils',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'pulses_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Pulses, nuts & seeds : beans, chickpeas, lentils',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Pulses, nuts & seeds : beans, chickpeas, lentils',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'pulses_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Broken pipes in the area',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Broken pipes in the area',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'broken_pipes'
                    },
                    {
                        'labelEn': 'Inability to pump water to the roof tanks',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Inability to pump water to the roof tanks',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'cannot_pump_water_to_rooftanks'
                    },
                    {
                        'labelEn': 'No more shop credit',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No more shop credit',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'no_shop_credit'
                    },
                    {
                        'labelEn': 'Not having adequate storage tanks',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not having adequate storage tanks',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'no_storage_tank'
                    },
                    {
                        'labelEn': 'Exceptional overconsumption',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Exceptional overconsumption',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'overconsumption'
                    },
                    {
                        'labelEn': 'Landlord cut supply',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Landlord cut supply',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'supply_cut_landlord'
                    },
                    {
                        'labelEn': 'Water authority cut supply',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Water authority cut supply',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'supply_cut_waterauthority'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What was/is the reason for not having water in your household?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What was/is the reason for not having water in your household?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'reason_no_water_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Has any child in the family had diarrhea (liquid stool more than 3 times a day) in the last 2 weeks?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Has any child in the family had diarrhea (liquid stool more than 3 times a day) in the last 2 weeks?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'recent_diarrehea_child_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Has any of your children been ill with cough and fever at any time in the last 2 weeks?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Has any of your children been ill with cough and fever at any time in the last 2 weeks?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'recent_illness_child_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': '0p. At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '0p. At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': '1p. Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '1p. Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    },
                    {
                        'labelEn': '2p. Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '2p. Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2.0'
                    },
                    {
                        'labelEn': '3p More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '3p More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3.0'
                    },
                    {
                        'labelEn': '4p. Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '4p. Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4.0'
                    },
                    {
                        'labelEn': '5p. All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': '5p. All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': '2. I have felt relaxed and calm',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': '2. I have felt relaxed and calm',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'relaxed_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'There are risks to children who get married before they are 18.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'There are risks to children who get married before they are 18.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'risk_early_marriage_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Rounded total expenses',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Rounded total expenses',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'round_total_expense_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Rounded total income',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Rounded total income',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'round_total_income_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If the individual is a child, does he/she ever been enrolled in school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If the individual is a child, does he/she ever been enrolled in school?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'school_enrolled_before_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If the individual is a child, does he/she currently enrolled in school',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If the individual is a child, does he/she currently enrolled in school',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'school_enrolled_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Is the child currently attending school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Is the child currently attending school?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'school_frequency_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Informal',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Informal',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'informal'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'other'
                    },
                    {
                        'labelEn': 'Private',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Private',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'private'
                    },
                    {
                        'labelEn': 'Public',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Public',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'public'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What type of school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What type of school?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'school_type_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'NFI score',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'NFI score',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'score_NFI_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Is there enough space or seat or handrail for a disabled person?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Is there enough space or seat or handrail for a disabled person?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'seat_handrail_for_disabled_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'no_overflow'
                    },
                    {
                        'labelEn': 'Yes because of Blockage/ broken connection/ overfilled spetage tank',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes because of Blockage/ broken connection/ overfilled spetage tank',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'yes_blockage'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Is there any sewage overflow from your latrine?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Is there any sewage overflow from your latrine?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'sewage_overflow_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Always',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Always',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_always'
                    },
                    {
                        'labelEn': 'Most of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Most of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_mostly'
                    },
                    {
                        'labelEn': 'Never',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Never',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_never'
                    },
                    {
                        'labelEn': 'Rarely',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rarely',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_rarely'
                    },
                    {
                        'labelEn': 'Sometimes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Sometimes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'level_sometimes'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'A survivor of sexual violence is not a shame to his or her family.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'A survivor of sexual violence is not a shame to his or her family.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'sexviolence_survivor_not_shame_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No facility (open defecation)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No facility (open defecation)',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'no_latrine'
                    },
                    {
                        'labelEn': 'No, only my household has access',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, only my household has access',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'not_shared'
                    },
                    {
                        'labelEn': 'Yes, with two or more households',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes, with two or more households',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'shared_with_one_hh'
                    },
                    {
                        'labelEn': 'Yes, with one other household',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes, with one other household',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'shared_with_two_hh'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Do you share a latrine?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Do you share a latrine?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'share_latrine_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Describe where:',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Describe where:',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'specify_where_night_i_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Spices, condiments and beverages',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Spices, condiments and beverages',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'spices_condiments_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No, everyday our family struggles because of lack of water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, everyday our family struggles because of lack of water',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'insufficientwater'
                    },
                    {
                        'labelEn': 'It is not always enough',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'It is not always enough',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'partiallysufficientwater'
                    },
                    {
                        'labelEn': 'Yes, it is sufficient for our needs',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes, it is sufficient for our needs',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'sufficientwater'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Is water sufficient for all your uses in the household?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Is water sufficient for all your uses in the household?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'sufficient_water_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Sugar / sweets: honey, cakes, sugary drinks, (this includes sugar used in tea)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Sugar / sweets: honey, cakes, sugary drinks, (this includes sugar used in tea)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'sugarsweet_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Sugar / sweets: honey, cakes, sugary drinks, (this includes sugar used in tea)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Sugar / sweets: honey, cakes, sugary drinks, (this includes sugar used in tea)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'sugarsweet_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the total number of people living in the dwelling?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the total number of people living in the dwelling?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'total_dwellers_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Total expenses',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Total expenses',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'total_expense_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Total number of households in the same living space?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Total number of households in the same living space?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'total_households_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Total income',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Total income',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'total_inc_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Total liters of water fetched yesterday (calculated)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Total liters of water fetched yesterday (calculated)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'total_liter_yesterday_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Transportation (to school, to health/rehab centers, to market, others)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Transportation (to school, to health/rehab centers, to market, others)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'transportation_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Treatment for children (medical, pharmaceutical)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Treatment for children (medical, pharmaceutical)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'treatment_child_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Government Hospital',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Government Hospital',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'governent_health_center'
                    },
                    {
                        'labelEn': 'Government Health Center',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Government Health Center',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'governent_hospital'
                    },
                    {
                        'labelEn': 'Other Private',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other Private',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'other_private'
                    },
                    {
                        'labelEn': 'Other Public',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other Public',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'other_public'
                    },
                    {
                        'labelEn': 'Pharmacy',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Pharmacy',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'pharmacy'
                    },
                    {
                        'labelEn': 'Private Doctor',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Private Doctor',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'private_doctor'
                    },
                    {
                        'labelEn': 'Private Hospital/Clinic',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Private Hospital/Clinic',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'private_hospital'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Where did you seek advice or treatment?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Where did you seek advice or treatment?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'treatment_facility_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If above is Yes, did you seek advice or treatment for the illness from any source?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If above is Yes, did you seek advice or treatment for the illness from any source?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'treatment_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How many trips did you make to fetch water yesterday?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many trips did you make to fetch water yesterday?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'trips_to_fetch_water_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'White tubers & roots: e.g potato, sweet potato, cassava, …',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'White tubers & roots: e.g potato, sweet potato, cassava, …',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'tubers_roots_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'White tubers & roots: e.g potato, sweet potato, cassava, …',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'White tubers & roots: e.g potato, sweet potato, cassava, …',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'tubers_roots_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Does your family host an unaccompanied child / fosterchild?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Does your family host an unaccompanied child / fosterchild?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'unaccompanied_child_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Vegetables & leaves: e.g spinach, cucumber, eggplant, tomato, …',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Vegetables & leaves: e.g spinach, cucumber, eggplant, tomato, …',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'vegetables_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': ''
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1.0'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Vegetables & leaves: e.g spinach, cucumber, eggplant, tomato, …',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Vegetables & leaves: e.g spinach, cucumber, eggplant, tomato, …',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'vegetables_hdds_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the volume of the container in liter in each trip?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the volume of the container in liter in each trip?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'volume_container_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Buy water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Buy water',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'buy_water'
                    },
                    {
                        'labelEn': 'Collector',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Collector',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'collect_water'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Do you buy or collect from this source?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Do you buy or collect from this source?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'washing_water_acquire_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Packaged water (bottled water, sachets_',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Packaged water (bottled water, sachets_',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'packaged_water'
                    },
                    {
                        'labelEn': 'Piped water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Piped water',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'piped_water'
                    },
                    {
                        'labelEn': 'From private vendor',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'From private vendor',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'private_vendor_water'
                    },
                    {
                        'labelEn': 'Rain water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rain water',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'rain_water'
                    },
                    {
                        'labelEn': 'Spring water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Spring water',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'spring_water'
                    },
                    {
                        'labelEn': 'Surface water (river, dam, lake, pond, canal, irrigation channel)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Surface water (river, dam, lake, pond, canal, irrigation channel)',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'surface_water'
                    },
                    {
                        'labelEn': 'Water tank',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Water tank',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'water_tank'
                    },
                    {
                        'labelEn': 'Water from a well',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Water from a well',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'well_water'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the primary source of water used by members of your household for other purposes such as cooking and handwashing?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the primary source of water used by members of your household for other purposes such as cooking and handwashing?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'washing_water_source_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Monthly',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Monthly',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'monthly_collect'
                    },
                    {
                        'labelEn': 'Twice a week',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Twice a week',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'twice_week_collect'
                    },
                    {
                        'labelEn': 'Weekly',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Weekly',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'weekly_collect'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How frequent solid waste collection is made?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How frequent solid waste collection is made?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'waste_collect_freq_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'no_disposal'
                    },
                    {
                        'labelEn': 'Yes. Bags',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes. Bags',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'yes_bags'
                    },
                    {
                        'labelEn': 'Yes. Bins',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes. Bins',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'yes_bins'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Do you have proper waste disposal?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Do you have proper waste disposal?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'waste_disposal_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Water (network, tanker, bottles etc)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Water (network, tanker, bottles etc)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'water_bottles_h_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Wellbeing Index',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Wellbeing Index',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'wellbeing_index_i_f',
                'required': False,
                'type': 'DECIMAL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How many years has the child been in school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many years has the child been in school?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'years_in_school_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Age (calculated)',
                'labels': [
                    {
                        'label': 'Age (calculated)',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'age',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Non-displaced  |   Host',
                        'labels': [
                            {
                                'label': 'Non-displaced  |   Host',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HOST'
                    },
                    {
                        'labelEn': 'Displaced  |  Internally Displaced People',
                        'labels': [
                            {
                                'label': 'Displaced  |  Internally Displaced People',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IDP'
                    },
                    {
                        'labelEn': 'Non-displaced  |   Non-host',
                        'labels': [
                            {
                                'label': 'Non-displaced  |   Non-host',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NON_HOST'
                    },
                    {
                        'labelEn': 'Displaced  |  Others of Concern',
                        'labels': [
                            {
                                'label': 'Displaced  |  Others of Concern',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'OTHERS_OF_CONCERN'
                    },
                    {
                        'labelEn': 'Displaced  |  Refugee / Asylum Seeker',
                        'labels': [
                            {
                                'label': 'Displaced  |  Refugee / Asylum Seeker',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'REFUGEE'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Residence status',
                'labels': [
                    {
                        'label': 'Residence status',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'residence_status',
                'required': True,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Aruba',
                        'labels': [
                            {
                                'label': 'Aruba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ABW'
                    },
                    {
                        'labelEn': 'Afghanistan',
                        'labels': [
                            {
                                'label': 'Afghanistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AFG'
                    },
                    {
                        'labelEn': 'Angola',
                        'labels': [
                            {
                                'label': 'Angola',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AGO'
                    },
                    {
                        'labelEn': 'Anguilla',
                        'labels': [
                            {
                                'label': 'Anguilla',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AIA'
                    },
                    {
                        'labelEn': 'Albania',
                        'labels': [
                            {
                                'label': 'Albania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ALB'
                    },
                    {
                        'labelEn': 'Andorra',
                        'labels': [
                            {
                                'label': 'Andorra',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AND'
                    },
                    {
                        'labelEn': 'Netherlands Antilles',
                        'labels': [
                            {
                                'label': 'Netherlands Antilles',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ANT'
                    },
                    {
                        'labelEn': 'United Arab Emirates',
                        'labels': [
                            {
                                'label': 'United Arab Emirates',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ARE'
                    },
                    {
                        'labelEn': 'Argentina',
                        'labels': [
                            {
                                'label': 'Argentina',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ARG'
                    },
                    {
                        'labelEn': 'Armenia',
                        'labels': [
                            {
                                'label': 'Armenia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ARM'
                    },
                    {
                        'labelEn': 'American Samoa',
                        'labels': [
                            {
                                'label': 'American Samoa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ASM'
                    },
                    {
                        'labelEn': 'Antarctica',
                        'labels': [
                            {
                                'label': 'Antarctica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ATA'
                    },
                    {
                        'labelEn': 'French Southern Territories',
                        'labels': [
                            {
                                'label': 'French Southern Territories',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ATF'
                    },
                    {
                        'labelEn': 'Antigua and Barbuda',
                        'labels': [
                            {
                                'label': 'Antigua and Barbuda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ATG'
                    },
                    {
                        'labelEn': 'Australia',
                        'labels': [
                            {
                                'label': 'Australia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AUS'
                    },
                    {
                        'labelEn': 'Austria',
                        'labels': [
                            {
                                'label': 'Austria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AUT'
                    },
                    {
                        'labelEn': 'Azerbaijan',
                        'labels': [
                            {
                                'label': 'Azerbaijan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AZE'
                    },
                    {
                        'labelEn': 'Burundi',
                        'labels': [
                            {
                                'label': 'Burundi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BDI'
                    },
                    {
                        'labelEn': 'Belgium',
                        'labels': [
                            {
                                'label': 'Belgium',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BEL'
                    },
                    {
                        'labelEn': 'Benin',
                        'labels': [
                            {
                                'label': 'Benin',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BEN'
                    },
                    {
                        'labelEn': 'Burkina Faso',
                        'labels': [
                            {
                                'label': 'Burkina Faso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BFA'
                    },
                    {
                        'labelEn': 'Bangladesh',
                        'labels': [
                            {
                                'label': 'Bangladesh',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BGD'
                    },
                    {
                        'labelEn': 'Bulgaria',
                        'labels': [
                            {
                                'label': 'Bulgaria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BGR'
                    },
                    {
                        'labelEn': 'Bahrain',
                        'labels': [
                            {
                                'label': 'Bahrain',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BHR'
                    },
                    {
                        'labelEn': 'Bahamas',
                        'labels': [
                            {
                                'label': 'Bahamas',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BHS'
                    },
                    {
                        'labelEn': 'Bosnia and Herzegovina',
                        'labels': [
                            {
                                'label': 'Bosnia and Herzegovina',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BIH'
                    },
                    {
                        'labelEn': 'Belarus',
                        'labels': [
                            {
                                'label': 'Belarus',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BLR'
                    },
                    {
                        'labelEn': 'Belize',
                        'labels': [
                            {
                                'label': 'Belize',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BLZ'
                    },
                    {
                        'labelEn': 'Bermuda',
                        'labels': [
                            {
                                'label': 'Bermuda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BMU'
                    },
                    {
                        'labelEn': 'Bolivia',
                        'labels': [
                            {
                                'label': 'Bolivia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BOL'
                    },
                    {
                        'labelEn': 'Brazil',
                        'labels': [
                            {
                                'label': 'Brazil',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BRA'
                    },
                    {
                        'labelEn': 'Barbados',
                        'labels': [
                            {
                                'label': 'Barbados',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BRB'
                    },
                    {
                        'labelEn': 'Brunei',
                        'labels': [
                            {
                                'label': 'Brunei',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BRN'
                    },
                    {
                        'labelEn': 'Bhutan',
                        'labels': [
                            {
                                'label': 'Bhutan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BTN'
                    },
                    {
                        'labelEn': 'Bouvet Island',
                        'labels': [
                            {
                                'label': 'Bouvet Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BVT'
                    },
                    {
                        'labelEn': 'Botswana',
                        'labels': [
                            {
                                'label': 'Botswana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BWA'
                    },
                    {
                        'labelEn': 'Central African Republic',
                        'labels': [
                            {
                                'label': 'Central African Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CAF'
                    },
                    {
                        'labelEn': 'Canada',
                        'labels': [
                            {
                                'label': 'Canada',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CAN'
                    },
                    {
                        'labelEn': 'Cocos (Keeling) Islands',
                        'labels': [
                            {
                                'label': 'Cocos (Keeling) Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CCK'
                    },
                    {
                        'labelEn': 'Switzerland',
                        'labels': [
                            {
                                'label': 'Switzerland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CHE'
                    },
                    {
                        'labelEn': 'Chile',
                        'labels': [
                            {
                                'label': 'Chile',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CHL'
                    },
                    {
                        'labelEn': 'China',
                        'labels': [
                            {
                                'label': 'China',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CHN'
                    },
                    {
                        'labelEn': 'Ivory Coast',
                        'labels': [
                            {
                                'label': 'Ivory Coast',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CIV'
                    },
                    {
                        'labelEn': 'Cameroon',
                        'labels': [
                            {
                                'label': 'Cameroon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CMR'
                    },
                    {
                        'labelEn': 'The Democratic Republic of the Congo',
                        'labels': [
                            {
                                'label': 'The Democratic Republic of the Congo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COD'
                    },
                    {
                        'labelEn': 'Congo',
                        'labels': [
                            {
                                'label': 'Congo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COG'
                    },
                    {
                        'labelEn': 'Cook Islands',
                        'labels': [
                            {
                                'label': 'Cook Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COK'
                    },
                    {
                        'labelEn': 'Colombia',
                        'labels': [
                            {
                                'label': 'Colombia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COL'
                    },
                    {
                        'labelEn': 'Comoros',
                        'labels': [
                            {
                                'label': 'Comoros',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COM'
                    },
                    {
                        'labelEn': 'Cape Verde',
                        'labels': [
                            {
                                'label': 'Cape Verde',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CPV'
                    },
                    {
                        'labelEn': 'Costa Rica',
                        'labels': [
                            {
                                'label': 'Costa Rica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CRI'
                    },
                    {
                        'labelEn': 'Cuba',
                        'labels': [
                            {
                                'label': 'Cuba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CUB'
                    },
                    {
                        'labelEn': 'Christmas Island',
                        'labels': [
                            {
                                'label': 'Christmas Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CXR'
                    },
                    {
                        'labelEn': 'Cayman Islands',
                        'labels': [
                            {
                                'label': 'Cayman Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CYM'
                    },
                    {
                        'labelEn': 'Cyprus',
                        'labels': [
                            {
                                'label': 'Cyprus',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CYP'
                    },
                    {
                        'labelEn': 'Czech Republic',
                        'labels': [
                            {
                                'label': 'Czech Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CZE'
                    },
                    {
                        'labelEn': 'Germany',
                        'labels': [
                            {
                                'label': 'Germany',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DEU'
                    },
                    {
                        'labelEn': 'Djibouti',
                        'labels': [
                            {
                                'label': 'Djibouti',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DJI'
                    },
                    {
                        'labelEn': 'Dominica',
                        'labels': [
                            {
                                'label': 'Dominica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DMA'
                    },
                    {
                        'labelEn': 'Denmark',
                        'labels': [
                            {
                                'label': 'Denmark',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DNK'
                    },
                    {
                        'labelEn': 'Dominican Republic',
                        'labels': [
                            {
                                'label': 'Dominican Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DOM'
                    },
                    {
                        'labelEn': 'Algeria',
                        'labels': [
                            {
                                'label': 'Algeria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DZA'
                    },
                    {
                        'labelEn': 'Ecuador',
                        'labels': [
                            {
                                'label': 'Ecuador',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ECU'
                    },
                    {
                        'labelEn': 'Egypt',
                        'labels': [
                            {
                                'label': 'Egypt',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EGY'
                    },
                    {
                        'labelEn': 'Eritrea',
                        'labels': [
                            {
                                'label': 'Eritrea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ERI'
                    },
                    {
                        'labelEn': 'Western Sahara',
                        'labels': [
                            {
                                'label': 'Western Sahara',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ESH'
                    },
                    {
                        'labelEn': 'Spain',
                        'labels': [
                            {
                                'label': 'Spain',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ESP'
                    },
                    {
                        'labelEn': 'Estonia',
                        'labels': [
                            {
                                'label': 'Estonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EST'
                    },
                    {
                        'labelEn': 'Ethiopia',
                        'labels': [
                            {
                                'label': 'Ethiopia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ETH'
                    },
                    {
                        'labelEn': 'Finland',
                        'labels': [
                            {
                                'label': 'Finland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FIN'
                    },
                    {
                        'labelEn': 'Fiji',
                        'labels': [
                            {
                                'label': 'Fiji',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FJI'
                    },
                    {
                        'labelEn': 'Falkland Islands (Malvinas)',
                        'labels': [
                            {
                                'label': 'Falkland Islands (Malvinas)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FLK'
                    },
                    {
                        'labelEn': 'France',
                        'labels': [
                            {
                                'label': 'France',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FRA'
                    },
                    {
                        'labelEn': 'Faroe Islands',
                        'labels': [
                            {
                                'label': 'Faroe Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FRO'
                    },
                    {
                        'labelEn': 'Federated States of Micronesia',
                        'labels': [
                            {
                                'label': 'Federated States of Micronesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FSM'
                    },
                    {
                        'labelEn': 'Gabon',
                        'labels': [
                            {
                                'label': 'Gabon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GAB'
                    },
                    {
                        'labelEn': 'United Kingdom',
                        'labels': [
                            {
                                'label': 'United Kingdom',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GBR'
                    },
                    {
                        'labelEn': 'Georgia',
                        'labels': [
                            {
                                'label': 'Georgia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GEO'
                    },
                    {
                        'labelEn': 'Guernsey',
                        'labels': [
                            {
                                'label': 'Guernsey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GGY'
                    },
                    {
                        'labelEn': 'Ghana',
                        'labels': [
                            {
                                'label': 'Ghana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GHA'
                    },
                    {
                        'labelEn': 'Gibraltar',
                        'labels': [
                            {
                                'label': 'Gibraltar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GIB'
                    },
                    {
                        'labelEn': 'Guinea',
                        'labels': [
                            {
                                'label': 'Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GIN'
                    },
                    {
                        'labelEn': 'Guadeloupe',
                        'labels': [
                            {
                                'label': 'Guadeloupe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GLP'
                    },
                    {
                        'labelEn': 'Gambia',
                        'labels': [
                            {
                                'label': 'Gambia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GMB'
                    },
                    {
                        'labelEn': 'Guinea-Bissau',
                        'labels': [
                            {
                                'label': 'Guinea-Bissau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GNB'
                    },
                    {
                        'labelEn': 'Equatorial Guinea',
                        'labels': [
                            {
                                'label': 'Equatorial Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GNQ'
                    },
                    {
                        'labelEn': 'Greece',
                        'labels': [
                            {
                                'label': 'Greece',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GRC'
                    },
                    {
                        'labelEn': 'Grenada',
                        'labels': [
                            {
                                'label': 'Grenada',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GRD'
                    },
                    {
                        'labelEn': 'Greenland',
                        'labels': [
                            {
                                'label': 'Greenland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GRL'
                    },
                    {
                        'labelEn': 'Guatemala',
                        'labels': [
                            {
                                'label': 'Guatemala',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GTM'
                    },
                    {
                        'labelEn': 'French Guiana',
                        'labels': [
                            {
                                'label': 'French Guiana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GUF'
                    },
                    {
                        'labelEn': 'Guam',
                        'labels': [
                            {
                                'label': 'Guam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GUM'
                    },
                    {
                        'labelEn': 'Guyana',
                        'labels': [
                            {
                                'label': 'Guyana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GUY'
                    },
                    {
                        'labelEn': 'Hong Kong',
                        'labels': [
                            {
                                'label': 'Hong Kong',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HKG'
                    },
                    {
                        'labelEn': 'Heard Island and McDonald Islands',
                        'labels': [
                            {
                                'label': 'Heard Island and McDonald Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HMD'
                    },
                    {
                        'labelEn': 'Honduras',
                        'labels': [
                            {
                                'label': 'Honduras',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HND'
                    },
                    {
                        'labelEn': 'Croatia',
                        'labels': [
                            {
                                'label': 'Croatia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HRV'
                    },
                    {
                        'labelEn': 'Haiti',
                        'labels': [
                            {
                                'label': 'Haiti',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HTI'
                    },
                    {
                        'labelEn': 'Hungary',
                        'labels': [
                            {
                                'label': 'Hungary',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HUN'
                    },
                    {
                        'labelEn': 'Indonesia',
                        'labels': [
                            {
                                'label': 'Indonesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IDN'
                    },
                    {
                        'labelEn': 'Isle of Man',
                        'labels': [
                            {
                                'label': 'Isle of Man',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IMN'
                    },
                    {
                        'labelEn': 'India',
                        'labels': [
                            {
                                'label': 'India',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IND'
                    },
                    {
                        'labelEn': 'British Indian Ocean Territory',
                        'labels': [
                            {
                                'label': 'British Indian Ocean Territory',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IOT'
                    },
                    {
                        'labelEn': 'Ireland',
                        'labels': [
                            {
                                'label': 'Ireland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IRL'
                    },
                    {
                        'labelEn': 'Iran, Islamic Republic of',
                        'labels': [
                            {
                                'label': 'Iran, Islamic Republic of',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IRN'
                    },
                    {
                        'labelEn': 'Iraq',
                        'labels': [
                            {
                                'label': 'Iraq',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IRQ'
                    },
                    {
                        'labelEn': 'Iceland',
                        'labels': [
                            {
                                'label': 'Iceland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ISL'
                    },
                    {
                        'labelEn': 'Israel',
                        'labels': [
                            {
                                'label': 'Israel',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ISR'
                    },
                    {
                        'labelEn': 'Italy',
                        'labels': [
                            {
                                'label': 'Italy',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ITA'
                    },
                    {
                        'labelEn': 'Jamaica',
                        'labels': [
                            {
                                'label': 'Jamaica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JAM'
                    },
                    {
                        'labelEn': 'Jersey',
                        'labels': [
                            {
                                'label': 'Jersey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JEY'
                    },
                    {
                        'labelEn': 'Jordan',
                        'labels': [
                            {
                                'label': 'Jordan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JOR'
                    },
                    {
                        'labelEn': 'Japan',
                        'labels': [
                            {
                                'label': 'Japan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JPN'
                    },
                    {
                        'labelEn': 'Kazakhstan',
                        'labels': [
                            {
                                'label': 'Kazakhstan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KAZ'
                    },
                    {
                        'labelEn': 'Kenya',
                        'labels': [
                            {
                                'label': 'Kenya',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KEN'
                    },
                    {
                        'labelEn': 'Kyrgyzstan',
                        'labels': [
                            {
                                'label': 'Kyrgyzstan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KGZ'
                    },
                    {
                        'labelEn': 'Cambodia',
                        'labels': [
                            {
                                'label': 'Cambodia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KHM'
                    },
                    {
                        'labelEn': 'Kiribati',
                        'labels': [
                            {
                                'label': 'Kiribati',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KIR'
                    },
                    {
                        'labelEn': 'Saint Kitts and Nevis',
                        'labels': [
                            {
                                'label': 'Saint Kitts and Nevis',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KNA'
                    },
                    {
                        'labelEn': 'South Korea',
                        'labels': [
                            {
                                'label': 'South Korea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KOR'
                    },
                    {
                        'labelEn': 'Kuwait',
                        'labels': [
                            {
                                'label': 'Kuwait',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KWT'
                    },
                    {
                        'labelEn': "Lao People's Democratic Republic",
                        'labels': [
                            {
                                'label': "Lao People's Democratic Republic",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LAO'
                    },
                    {
                        'labelEn': 'Lebanon',
                        'labels': [
                            {
                                'label': 'Lebanon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LBN'
                    },
                    {
                        'labelEn': 'Liberia',
                        'labels': [
                            {
                                'label': 'Liberia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LBR'
                    },
                    {
                        'labelEn': 'Libya',
                        'labels': [
                            {
                                'label': 'Libya',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LBY'
                    },
                    {
                        'labelEn': 'Saint Lucia',
                        'labels': [
                            {
                                'label': 'Saint Lucia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LCA'
                    },
                    {
                        'labelEn': 'Liechtenstein',
                        'labels': [
                            {
                                'label': 'Liechtenstein',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LIE'
                    },
                    {
                        'labelEn': 'Sri Lanka',
                        'labels': [
                            {
                                'label': 'Sri Lanka',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LKA'
                    },
                    {
                        'labelEn': 'Lesotho',
                        'labels': [
                            {
                                'label': 'Lesotho',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LSO'
                    },
                    {
                        'labelEn': 'Lithuania',
                        'labels': [
                            {
                                'label': 'Lithuania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LTU'
                    },
                    {
                        'labelEn': 'Luxembourg',
                        'labels': [
                            {
                                'label': 'Luxembourg',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LUX'
                    },
                    {
                        'labelEn': 'Latvia',
                        'labels': [
                            {
                                'label': 'Latvia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LVA'
                    },
                    {
                        'labelEn': 'Macao',
                        'labels': [
                            {
                                'label': 'Macao',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MAC'
                    },
                    {
                        'labelEn': 'Morocco',
                        'labels': [
                            {
                                'label': 'Morocco',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MAR'
                    },
                    {
                        'labelEn': 'Monaco',
                        'labels': [
                            {
                                'label': 'Monaco',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MCO'
                    },
                    {
                        'labelEn': 'Republic of Moldova',
                        'labels': [
                            {
                                'label': 'Republic of Moldova',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MDA'
                    },
                    {
                        'labelEn': 'Madagascar',
                        'labels': [
                            {
                                'label': 'Madagascar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MDG'
                    },
                    {
                        'labelEn': 'Maldives',
                        'labels': [
                            {
                                'label': 'Maldives',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MDV'
                    },
                    {
                        'labelEn': 'Mexico',
                        'labels': [
                            {
                                'label': 'Mexico',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MEX'
                    },
                    {
                        'labelEn': 'Marshall Islands',
                        'labels': [
                            {
                                'label': 'Marshall Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MHL'
                    },
                    {
                        'labelEn': 'Republic of North Macedonia',
                        'labels': [
                            {
                                'label': 'Republic of North Macedonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MKD'
                    },
                    {
                        'labelEn': 'Mali',
                        'labels': [
                            {
                                'label': 'Mali',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MLI'
                    },
                    {
                        'labelEn': 'Malta',
                        'labels': [
                            {
                                'label': 'Malta',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MLT'
                    },
                    {
                        'labelEn': 'Myanmar',
                        'labels': [
                            {
                                'label': 'Myanmar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MMR'
                    },
                    {
                        'labelEn': 'Montenegro',
                        'labels': [
                            {
                                'label': 'Montenegro',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MNE'
                    },
                    {
                        'labelEn': 'Mongolia',
                        'labels': [
                            {
                                'label': 'Mongolia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MNG'
                    },
                    {
                        'labelEn': 'Northern Mariana Islands',
                        'labels': [
                            {
                                'label': 'Northern Mariana Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MNP'
                    },
                    {
                        'labelEn': 'Mozambique',
                        'labels': [
                            {
                                'label': 'Mozambique',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MOZ'
                    },
                    {
                        'labelEn': 'Mauritania',
                        'labels': [
                            {
                                'label': 'Mauritania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MRT'
                    },
                    {
                        'labelEn': 'Montserrat',
                        'labels': [
                            {
                                'label': 'Montserrat',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MSR'
                    },
                    {
                        'labelEn': 'Martinique',
                        'labels': [
                            {
                                'label': 'Martinique',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MTQ'
                    },
                    {
                        'labelEn': 'Mauritius',
                        'labels': [
                            {
                                'label': 'Mauritius',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MUS'
                    },
                    {
                        'labelEn': 'Malawi',
                        'labels': [
                            {
                                'label': 'Malawi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MWI'
                    },
                    {
                        'labelEn': 'Malaysia',
                        'labels': [
                            {
                                'label': 'Malaysia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MYS'
                    },
                    {
                        'labelEn': 'Mayotte',
                        'labels': [
                            {
                                'label': 'Mayotte',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MYT'
                    },
                    {
                        'labelEn': 'Namibia',
                        'labels': [
                            {
                                'label': 'Namibia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NAM'
                    },
                    {
                        'labelEn': 'New Caledonia',
                        'labels': [
                            {
                                'label': 'New Caledonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NCL'
                    },
                    {
                        'labelEn': 'Niger',
                        'labels': [
                            {
                                'label': 'Niger',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NER'
                    },
                    {
                        'labelEn': 'Norfolk Island',
                        'labels': [
                            {
                                'label': 'Norfolk Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NFK'
                    },
                    {
                        'labelEn': 'Nigeria',
                        'labels': [
                            {
                                'label': 'Nigeria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NGA'
                    },
                    {
                        'labelEn': 'Nicaragua',
                        'labels': [
                            {
                                'label': 'Nicaragua',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NIC'
                    },
                    {
                        'labelEn': 'Niue',
                        'labels': [
                            {
                                'label': 'Niue',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NIU'
                    },
                    {
                        'labelEn': 'Netherlands',
                        'labels': [
                            {
                                'label': 'Netherlands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NLD'
                    },
                    {
                        'labelEn': 'Norway',
                        'labels': [
                            {
                                'label': 'Norway',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NOR'
                    },
                    {
                        'labelEn': 'Nepal',
                        'labels': [
                            {
                                'label': 'Nepal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NPL'
                    },
                    {
                        'labelEn': 'Nauru',
                        'labels': [
                            {
                                'label': 'Nauru',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NRU'
                    },
                    {
                        'labelEn': 'New Zealand',
                        'labels': [
                            {
                                'label': 'New Zealand',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NZL'
                    },
                    {
                        'labelEn': 'Oman',
                        'labels': [
                            {
                                'label': 'Oman',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'OMN'
                    },
                    {
                        'labelEn': 'Pakistan',
                        'labels': [
                            {
                                'label': 'Pakistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PAK'
                    },
                    {
                        'labelEn': 'Panama',
                        'labels': [
                            {
                                'label': 'Panama',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PAN'
                    },
                    {
                        'labelEn': 'Pitcairn',
                        'labels': [
                            {
                                'label': 'Pitcairn',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PCN'
                    },
                    {
                        'labelEn': 'Peru',
                        'labels': [
                            {
                                'label': 'Peru',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PER'
                    },
                    {
                        'labelEn': 'Philippines',
                        'labels': [
                            {
                                'label': 'Philippines',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PHL'
                    },
                    {
                        'labelEn': 'Palau',
                        'labels': [
                            {
                                'label': 'Palau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PLW'
                    },
                    {
                        'labelEn': 'Papua New Guinea',
                        'labels': [
                            {
                                'label': 'Papua New Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PNG'
                    },
                    {
                        'labelEn': 'Poland',
                        'labels': [
                            {
                                'label': 'Poland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'POL'
                    },
                    {
                        'labelEn': 'Puerto Rico',
                        'labels': [
                            {
                                'label': 'Puerto Rico',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRI'
                    },
                    {
                        'labelEn': "Democratic People's Republic of Korea",
                        'labels': [
                            {
                                'label': "Democratic People's Republic of Korea",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRK'
                    },
                    {
                        'labelEn': 'Portugal',
                        'labels': [
                            {
                                'label': 'Portugal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRT'
                    },
                    {
                        'labelEn': 'Paraguay',
                        'labels': [
                            {
                                'label': 'Paraguay',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRY'
                    },
                    {
                        'labelEn': 'Palestinian Territory, Occupied',
                        'labels': [
                            {
                                'label': 'Palestinian Territory, Occupied',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PSE'
                    },
                    {
                        'labelEn': 'French Polynesia',
                        'labels': [
                            {
                                'label': 'French Polynesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PYF'
                    },
                    {
                        'labelEn': 'Qatar',
                        'labels': [
                            {
                                'label': 'Qatar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'QAT'
                    },
                    {
                        'labelEn': 'Réunion',
                        'labels': [
                            {
                                'label': 'Réunion',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'REU'
                    },
                    {
                        'labelEn': 'Romania',
                        'labels': [
                            {
                                'label': 'Romania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ROU'
                    },
                    {
                        'labelEn': 'Russia',
                        'labels': [
                            {
                                'label': 'Russia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RUS'
                    },
                    {
                        'labelEn': 'Rwanda',
                        'labels': [
                            {
                                'label': 'Rwanda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RWA'
                    },
                    {
                        'labelEn': 'Saudi Arabia',
                        'labels': [
                            {
                                'label': 'Saudi Arabia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SAU'
                    },
                    {
                        'labelEn': 'Sudan',
                        'labels': [
                            {
                                'label': 'Sudan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SDN'
                    },
                    {
                        'labelEn': 'Senegal',
                        'labels': [
                            {
                                'label': 'Senegal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SEN'
                    },
                    {
                        'labelEn': 'Singapore',
                        'labels': [
                            {
                                'label': 'Singapore',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SGP'
                    },
                    {
                        'labelEn': 'South Georgia and the South Sandwich Islands',
                        'labels': [
                            {
                                'label': 'South Georgia and the South Sandwich Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SGS'
                    },
                    {
                        'labelEn': 'Saint Helena, Ascension and Tristan da Cunha',
                        'labels': [
                            {
                                'label': 'Saint Helena, Ascension and Tristan da Cunha',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SHN'
                    },
                    {
                        'labelEn': 'Svalbard and Jan Mayen',
                        'labels': [
                            {
                                'label': 'Svalbard and Jan Mayen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SJM'
                    },
                    {
                        'labelEn': 'Solomon Islands',
                        'labels': [
                            {
                                'label': 'Solomon Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SLB'
                    },
                    {
                        'labelEn': 'Sierra Leone',
                        'labels': [
                            {
                                'label': 'Sierra Leone',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SLE'
                    },
                    {
                        'labelEn': 'El Salvador',
                        'labels': [
                            {
                                'label': 'El Salvador',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SLV'
                    },
                    {
                        'labelEn': 'San Marino',
                        'labels': [
                            {
                                'label': 'San Marino',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SMR'
                    },
                    {
                        'labelEn': 'Somalia',
                        'labels': [
                            {
                                'label': 'Somalia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SOM'
                    },
                    {
                        'labelEn': 'Saint Pierre and Miquelon',
                        'labels': [
                            {
                                'label': 'Saint Pierre and Miquelon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SPM'
                    },
                    {
                        'labelEn': 'Serbia',
                        'labels': [
                            {
                                'label': 'Serbia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SRB'
                    },
                    {
                        'labelEn': 'South Sudan',
                        'labels': [
                            {
                                'label': 'South Sudan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SSD'
                    },
                    {
                        'labelEn': 'Sao Tome and Principe',
                        'labels': [
                            {
                                'label': 'Sao Tome and Principe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'STP'
                    },
                    {
                        'labelEn': 'Suriname',
                        'labels': [
                            {
                                'label': 'Suriname',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SUR'
                    },
                    {
                        'labelEn': 'Slovakia',
                        'labels': [
                            {
                                'label': 'Slovakia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SVK'
                    },
                    {
                        'labelEn': 'Slovenia',
                        'labels': [
                            {
                                'label': 'Slovenia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SVN'
                    },
                    {
                        'labelEn': 'Sweden',
                        'labels': [
                            {
                                'label': 'Sweden',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SWE'
                    },
                    {
                        'labelEn': 'Swaziland',
                        'labels': [
                            {
                                'label': 'Swaziland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SWZ'
                    },
                    {
                        'labelEn': 'Seychelles',
                        'labels': [
                            {
                                'label': 'Seychelles',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SYC'
                    },
                    {
                        'labelEn': 'Syrian Arab Republic',
                        'labels': [
                            {
                                'label': 'Syrian Arab Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SYR'
                    },
                    {
                        'labelEn': 'Turks and Caicos Islands',
                        'labels': [
                            {
                                'label': 'Turks and Caicos Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TCA'
                    },
                    {
                        'labelEn': 'Chad',
                        'labels': [
                            {
                                'label': 'Chad',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TCD'
                    },
                    {
                        'labelEn': 'Togo',
                        'labels': [
                            {
                                'label': 'Togo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TGO'
                    },
                    {
                        'labelEn': 'Thailand',
                        'labels': [
                            {
                                'label': 'Thailand',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'THA'
                    },
                    {
                        'labelEn': 'Tajikistan',
                        'labels': [
                            {
                                'label': 'Tajikistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TJK'
                    },
                    {
                        'labelEn': 'Tokelau',
                        'labels': [
                            {
                                'label': 'Tokelau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TKL'
                    },
                    {
                        'labelEn': 'Turkmenistan',
                        'labels': [
                            {
                                'label': 'Turkmenistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TKM'
                    },
                    {
                        'labelEn': 'Timor-Leste',
                        'labels': [
                            {
                                'label': 'Timor-Leste',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TLS'
                    },
                    {
                        'labelEn': 'Tonga',
                        'labels': [
                            {
                                'label': 'Tonga',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TON'
                    },
                    {
                        'labelEn': 'Trinidad and Tobago',
                        'labels': [
                            {
                                'label': 'Trinidad and Tobago',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TTO'
                    },
                    {
                        'labelEn': 'Tunisia',
                        'labels': [
                            {
                                'label': 'Tunisia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TUN'
                    },
                    {
                        'labelEn': 'Turkey',
                        'labels': [
                            {
                                'label': 'Turkey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TUR'
                    },
                    {
                        'labelEn': 'Tuvalu',
                        'labels': [
                            {
                                'label': 'Tuvalu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TUV'
                    },
                    {
                        'labelEn': 'Taiwan',
                        'labels': [
                            {
                                'label': 'Taiwan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TWN'
                    },
                    {
                        'labelEn': 'Tanzania, United Republic of',
                        'labels': [
                            {
                                'label': 'Tanzania, United Republic of',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TZA'
                    },
                    {
                        'labelEn': 'Uganda',
                        'labels': [
                            {
                                'label': 'Uganda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UGA'
                    },
                    {
                        'labelEn': 'Ukraine',
                        'labels': [
                            {
                                'label': 'Ukraine',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UKR'
                    },
                    {
                        'labelEn': 'United States Minor Outlying Islands',
                        'labels': [
                            {
                                'label': 'United States Minor Outlying Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UMI'
                    },
                    {
                        'labelEn': 'Uruguay',
                        'labels': [
                            {
                                'label': 'Uruguay',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'URY'
                    },
                    {
                        'labelEn': 'United States',
                        'labels': [
                            {
                                'label': 'United States',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'USA'
                    },
                    {
                        'labelEn': 'Uzbekistan',
                        'labels': [
                            {
                                'label': 'Uzbekistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UZB'
                    },
                    {
                        'labelEn': 'Holy See (Vatican City State)',
                        'labels': [
                            {
                                'label': 'Holy See (Vatican City State)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VAT'
                    },
                    {
                        'labelEn': 'Saint Vincent and the Grenadines',
                        'labels': [
                            {
                                'label': 'Saint Vincent and the Grenadines',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VCT'
                    },
                    {
                        'labelEn': 'Venezuela',
                        'labels': [
                            {
                                'label': 'Venezuela',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VEN'
                    },
                    {
                        'labelEn': 'Virgin Islands, British',
                        'labels': [
                            {
                                'label': 'Virgin Islands, British',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VGB'
                    },
                    {
                        'labelEn': 'Virgin Islands, U.S.',
                        'labels': [
                            {
                                'label': 'Virgin Islands, U.S.',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VIR'
                    },
                    {
                        'labelEn': 'Vietnam',
                        'labels': [
                            {
                                'label': 'Vietnam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VNM'
                    },
                    {
                        'labelEn': 'Vanuatu',
                        'labels': [
                            {
                                'label': 'Vanuatu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VUT'
                    },
                    {
                        'labelEn': 'Wallis and Futuna',
                        'labels': [
                            {
                                'label': 'Wallis and Futuna',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WLF'
                    },
                    {
                        'labelEn': 'Samoa',
                        'labels': [
                            {
                                'label': 'Samoa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WSM'
                    },
                    {
                        'labelEn': 'Yemen',
                        'labels': [
                            {
                                'label': 'Yemen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'YEM'
                    },
                    {
                        'labelEn': 'South Africa',
                        'labels': [
                            {
                                'label': 'South Africa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZAF'
                    },
                    {
                        'labelEn': 'Zambia',
                        'labels': [
                            {
                                'label': 'Zambia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZMB'
                    },
                    {
                        'labelEn': 'Zimbabwe',
                        'labels': [
                            {
                                'label': 'Zimbabwe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZWE'
                    }
                ],
                'hint': 'country origin',
                'isFlexField': False,
                'labelEn': 'Country origin',
                'labels': [
                    {
                        'label': 'Country origin',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'country_origin',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Aruba',
                        'labels': [
                            {
                                'label': 'Aruba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ABW'
                    },
                    {
                        'labelEn': 'Afghanistan',
                        'labels': [
                            {
                                'label': 'Afghanistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AFG'
                    },
                    {
                        'labelEn': 'Angola',
                        'labels': [
                            {
                                'label': 'Angola',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AGO'
                    },
                    {
                        'labelEn': 'Anguilla',
                        'labels': [
                            {
                                'label': 'Anguilla',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AIA'
                    },
                    {
                        'labelEn': 'Albania',
                        'labels': [
                            {
                                'label': 'Albania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ALB'
                    },
                    {
                        'labelEn': 'Andorra',
                        'labels': [
                            {
                                'label': 'Andorra',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AND'
                    },
                    {
                        'labelEn': 'Netherlands Antilles',
                        'labels': [
                            {
                                'label': 'Netherlands Antilles',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ANT'
                    },
                    {
                        'labelEn': 'United Arab Emirates',
                        'labels': [
                            {
                                'label': 'United Arab Emirates',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ARE'
                    },
                    {
                        'labelEn': 'Argentina',
                        'labels': [
                            {
                                'label': 'Argentina',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ARG'
                    },
                    {
                        'labelEn': 'Armenia',
                        'labels': [
                            {
                                'label': 'Armenia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ARM'
                    },
                    {
                        'labelEn': 'American Samoa',
                        'labels': [
                            {
                                'label': 'American Samoa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ASM'
                    },
                    {
                        'labelEn': 'Antarctica',
                        'labels': [
                            {
                                'label': 'Antarctica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ATA'
                    },
                    {
                        'labelEn': 'French Southern Territories',
                        'labels': [
                            {
                                'label': 'French Southern Territories',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ATF'
                    },
                    {
                        'labelEn': 'Antigua and Barbuda',
                        'labels': [
                            {
                                'label': 'Antigua and Barbuda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ATG'
                    },
                    {
                        'labelEn': 'Australia',
                        'labels': [
                            {
                                'label': 'Australia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AUS'
                    },
                    {
                        'labelEn': 'Austria',
                        'labels': [
                            {
                                'label': 'Austria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AUT'
                    },
                    {
                        'labelEn': 'Azerbaijan',
                        'labels': [
                            {
                                'label': 'Azerbaijan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AZE'
                    },
                    {
                        'labelEn': 'Burundi',
                        'labels': [
                            {
                                'label': 'Burundi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BDI'
                    },
                    {
                        'labelEn': 'Belgium',
                        'labels': [
                            {
                                'label': 'Belgium',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BEL'
                    },
                    {
                        'labelEn': 'Benin',
                        'labels': [
                            {
                                'label': 'Benin',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BEN'
                    },
                    {
                        'labelEn': 'Burkina Faso',
                        'labels': [
                            {
                                'label': 'Burkina Faso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BFA'
                    },
                    {
                        'labelEn': 'Bangladesh',
                        'labels': [
                            {
                                'label': 'Bangladesh',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BGD'
                    },
                    {
                        'labelEn': 'Bulgaria',
                        'labels': [
                            {
                                'label': 'Bulgaria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BGR'
                    },
                    {
                        'labelEn': 'Bahrain',
                        'labels': [
                            {
                                'label': 'Bahrain',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BHR'
                    },
                    {
                        'labelEn': 'Bahamas',
                        'labels': [
                            {
                                'label': 'Bahamas',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BHS'
                    },
                    {
                        'labelEn': 'Bosnia and Herzegovina',
                        'labels': [
                            {
                                'label': 'Bosnia and Herzegovina',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BIH'
                    },
                    {
                        'labelEn': 'Belarus',
                        'labels': [
                            {
                                'label': 'Belarus',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BLR'
                    },
                    {
                        'labelEn': 'Belize',
                        'labels': [
                            {
                                'label': 'Belize',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BLZ'
                    },
                    {
                        'labelEn': 'Bermuda',
                        'labels': [
                            {
                                'label': 'Bermuda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BMU'
                    },
                    {
                        'labelEn': 'Bolivia',
                        'labels': [
                            {
                                'label': 'Bolivia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BOL'
                    },
                    {
                        'labelEn': 'Brazil',
                        'labels': [
                            {
                                'label': 'Brazil',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BRA'
                    },
                    {
                        'labelEn': 'Barbados',
                        'labels': [
                            {
                                'label': 'Barbados',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BRB'
                    },
                    {
                        'labelEn': 'Brunei',
                        'labels': [
                            {
                                'label': 'Brunei',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BRN'
                    },
                    {
                        'labelEn': 'Bhutan',
                        'labels': [
                            {
                                'label': 'Bhutan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BTN'
                    },
                    {
                        'labelEn': 'Bouvet Island',
                        'labels': [
                            {
                                'label': 'Bouvet Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BVT'
                    },
                    {
                        'labelEn': 'Botswana',
                        'labels': [
                            {
                                'label': 'Botswana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BWA'
                    },
                    {
                        'labelEn': 'Central African Republic',
                        'labels': [
                            {
                                'label': 'Central African Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CAF'
                    },
                    {
                        'labelEn': 'Canada',
                        'labels': [
                            {
                                'label': 'Canada',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CAN'
                    },
                    {
                        'labelEn': 'Cocos (Keeling) Islands',
                        'labels': [
                            {
                                'label': 'Cocos (Keeling) Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CCK'
                    },
                    {
                        'labelEn': 'Switzerland',
                        'labels': [
                            {
                                'label': 'Switzerland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CHE'
                    },
                    {
                        'labelEn': 'Chile',
                        'labels': [
                            {
                                'label': 'Chile',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CHL'
                    },
                    {
                        'labelEn': 'China',
                        'labels': [
                            {
                                'label': 'China',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CHN'
                    },
                    {
                        'labelEn': 'Ivory Coast',
                        'labels': [
                            {
                                'label': 'Ivory Coast',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CIV'
                    },
                    {
                        'labelEn': 'Cameroon',
                        'labels': [
                            {
                                'label': 'Cameroon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CMR'
                    },
                    {
                        'labelEn': 'The Democratic Republic of the Congo',
                        'labels': [
                            {
                                'label': 'The Democratic Republic of the Congo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COD'
                    },
                    {
                        'labelEn': 'Congo',
                        'labels': [
                            {
                                'label': 'Congo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COG'
                    },
                    {
                        'labelEn': 'Cook Islands',
                        'labels': [
                            {
                                'label': 'Cook Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COK'
                    },
                    {
                        'labelEn': 'Colombia',
                        'labels': [
                            {
                                'label': 'Colombia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COL'
                    },
                    {
                        'labelEn': 'Comoros',
                        'labels': [
                            {
                                'label': 'Comoros',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COM'
                    },
                    {
                        'labelEn': 'Cape Verde',
                        'labels': [
                            {
                                'label': 'Cape Verde',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CPV'
                    },
                    {
                        'labelEn': 'Costa Rica',
                        'labels': [
                            {
                                'label': 'Costa Rica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CRI'
                    },
                    {
                        'labelEn': 'Cuba',
                        'labels': [
                            {
                                'label': 'Cuba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CUB'
                    },
                    {
                        'labelEn': 'Christmas Island',
                        'labels': [
                            {
                                'label': 'Christmas Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CXR'
                    },
                    {
                        'labelEn': 'Cayman Islands',
                        'labels': [
                            {
                                'label': 'Cayman Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CYM'
                    },
                    {
                        'labelEn': 'Cyprus',
                        'labels': [
                            {
                                'label': 'Cyprus',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CYP'
                    },
                    {
                        'labelEn': 'Czech Republic',
                        'labels': [
                            {
                                'label': 'Czech Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CZE'
                    },
                    {
                        'labelEn': 'Germany',
                        'labels': [
                            {
                                'label': 'Germany',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DEU'
                    },
                    {
                        'labelEn': 'Djibouti',
                        'labels': [
                            {
                                'label': 'Djibouti',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DJI'
                    },
                    {
                        'labelEn': 'Dominica',
                        'labels': [
                            {
                                'label': 'Dominica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DMA'
                    },
                    {
                        'labelEn': 'Denmark',
                        'labels': [
                            {
                                'label': 'Denmark',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DNK'
                    },
                    {
                        'labelEn': 'Dominican Republic',
                        'labels': [
                            {
                                'label': 'Dominican Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DOM'
                    },
                    {
                        'labelEn': 'Algeria',
                        'labels': [
                            {
                                'label': 'Algeria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DZA'
                    },
                    {
                        'labelEn': 'Ecuador',
                        'labels': [
                            {
                                'label': 'Ecuador',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ECU'
                    },
                    {
                        'labelEn': 'Egypt',
                        'labels': [
                            {
                                'label': 'Egypt',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EGY'
                    },
                    {
                        'labelEn': 'Eritrea',
                        'labels': [
                            {
                                'label': 'Eritrea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ERI'
                    },
                    {
                        'labelEn': 'Western Sahara',
                        'labels': [
                            {
                                'label': 'Western Sahara',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ESH'
                    },
                    {
                        'labelEn': 'Spain',
                        'labels': [
                            {
                                'label': 'Spain',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ESP'
                    },
                    {
                        'labelEn': 'Estonia',
                        'labels': [
                            {
                                'label': 'Estonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EST'
                    },
                    {
                        'labelEn': 'Ethiopia',
                        'labels': [
                            {
                                'label': 'Ethiopia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ETH'
                    },
                    {
                        'labelEn': 'Finland',
                        'labels': [
                            {
                                'label': 'Finland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FIN'
                    },
                    {
                        'labelEn': 'Fiji',
                        'labels': [
                            {
                                'label': 'Fiji',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FJI'
                    },
                    {
                        'labelEn': 'Falkland Islands (Malvinas)',
                        'labels': [
                            {
                                'label': 'Falkland Islands (Malvinas)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FLK'
                    },
                    {
                        'labelEn': 'France',
                        'labels': [
                            {
                                'label': 'France',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FRA'
                    },
                    {
                        'labelEn': 'Faroe Islands',
                        'labels': [
                            {
                                'label': 'Faroe Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FRO'
                    },
                    {
                        'labelEn': 'Federated States of Micronesia',
                        'labels': [
                            {
                                'label': 'Federated States of Micronesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FSM'
                    },
                    {
                        'labelEn': 'Gabon',
                        'labels': [
                            {
                                'label': 'Gabon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GAB'
                    },
                    {
                        'labelEn': 'United Kingdom',
                        'labels': [
                            {
                                'label': 'United Kingdom',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GBR'
                    },
                    {
                        'labelEn': 'Georgia',
                        'labels': [
                            {
                                'label': 'Georgia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GEO'
                    },
                    {
                        'labelEn': 'Guernsey',
                        'labels': [
                            {
                                'label': 'Guernsey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GGY'
                    },
                    {
                        'labelEn': 'Ghana',
                        'labels': [
                            {
                                'label': 'Ghana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GHA'
                    },
                    {
                        'labelEn': 'Gibraltar',
                        'labels': [
                            {
                                'label': 'Gibraltar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GIB'
                    },
                    {
                        'labelEn': 'Guinea',
                        'labels': [
                            {
                                'label': 'Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GIN'
                    },
                    {
                        'labelEn': 'Guadeloupe',
                        'labels': [
                            {
                                'label': 'Guadeloupe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GLP'
                    },
                    {
                        'labelEn': 'Gambia',
                        'labels': [
                            {
                                'label': 'Gambia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GMB'
                    },
                    {
                        'labelEn': 'Guinea-Bissau',
                        'labels': [
                            {
                                'label': 'Guinea-Bissau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GNB'
                    },
                    {
                        'labelEn': 'Equatorial Guinea',
                        'labels': [
                            {
                                'label': 'Equatorial Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GNQ'
                    },
                    {
                        'labelEn': 'Greece',
                        'labels': [
                            {
                                'label': 'Greece',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GRC'
                    },
                    {
                        'labelEn': 'Grenada',
                        'labels': [
                            {
                                'label': 'Grenada',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GRD'
                    },
                    {
                        'labelEn': 'Greenland',
                        'labels': [
                            {
                                'label': 'Greenland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GRL'
                    },
                    {
                        'labelEn': 'Guatemala',
                        'labels': [
                            {
                                'label': 'Guatemala',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GTM'
                    },
                    {
                        'labelEn': 'French Guiana',
                        'labels': [
                            {
                                'label': 'French Guiana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GUF'
                    },
                    {
                        'labelEn': 'Guam',
                        'labels': [
                            {
                                'label': 'Guam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GUM'
                    },
                    {
                        'labelEn': 'Guyana',
                        'labels': [
                            {
                                'label': 'Guyana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GUY'
                    },
                    {
                        'labelEn': 'Hong Kong',
                        'labels': [
                            {
                                'label': 'Hong Kong',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HKG'
                    },
                    {
                        'labelEn': 'Heard Island and McDonald Islands',
                        'labels': [
                            {
                                'label': 'Heard Island and McDonald Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HMD'
                    },
                    {
                        'labelEn': 'Honduras',
                        'labels': [
                            {
                                'label': 'Honduras',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HND'
                    },
                    {
                        'labelEn': 'Croatia',
                        'labels': [
                            {
                                'label': 'Croatia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HRV'
                    },
                    {
                        'labelEn': 'Haiti',
                        'labels': [
                            {
                                'label': 'Haiti',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HTI'
                    },
                    {
                        'labelEn': 'Hungary',
                        'labels': [
                            {
                                'label': 'Hungary',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HUN'
                    },
                    {
                        'labelEn': 'Indonesia',
                        'labels': [
                            {
                                'label': 'Indonesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IDN'
                    },
                    {
                        'labelEn': 'Isle of Man',
                        'labels': [
                            {
                                'label': 'Isle of Man',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IMN'
                    },
                    {
                        'labelEn': 'India',
                        'labels': [
                            {
                                'label': 'India',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IND'
                    },
                    {
                        'labelEn': 'British Indian Ocean Territory',
                        'labels': [
                            {
                                'label': 'British Indian Ocean Territory',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IOT'
                    },
                    {
                        'labelEn': 'Ireland',
                        'labels': [
                            {
                                'label': 'Ireland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IRL'
                    },
                    {
                        'labelEn': 'Iran, Islamic Republic of',
                        'labels': [
                            {
                                'label': 'Iran, Islamic Republic of',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IRN'
                    },
                    {
                        'labelEn': 'Iraq',
                        'labels': [
                            {
                                'label': 'Iraq',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IRQ'
                    },
                    {
                        'labelEn': 'Iceland',
                        'labels': [
                            {
                                'label': 'Iceland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ISL'
                    },
                    {
                        'labelEn': 'Israel',
                        'labels': [
                            {
                                'label': 'Israel',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ISR'
                    },
                    {
                        'labelEn': 'Italy',
                        'labels': [
                            {
                                'label': 'Italy',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ITA'
                    },
                    {
                        'labelEn': 'Jamaica',
                        'labels': [
                            {
                                'label': 'Jamaica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JAM'
                    },
                    {
                        'labelEn': 'Jersey',
                        'labels': [
                            {
                                'label': 'Jersey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JEY'
                    },
                    {
                        'labelEn': 'Jordan',
                        'labels': [
                            {
                                'label': 'Jordan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JOR'
                    },
                    {
                        'labelEn': 'Japan',
                        'labels': [
                            {
                                'label': 'Japan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JPN'
                    },
                    {
                        'labelEn': 'Kazakhstan',
                        'labels': [
                            {
                                'label': 'Kazakhstan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KAZ'
                    },
                    {
                        'labelEn': 'Kenya',
                        'labels': [
                            {
                                'label': 'Kenya',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KEN'
                    },
                    {
                        'labelEn': 'Kyrgyzstan',
                        'labels': [
                            {
                                'label': 'Kyrgyzstan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KGZ'
                    },
                    {
                        'labelEn': 'Cambodia',
                        'labels': [
                            {
                                'label': 'Cambodia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KHM'
                    },
                    {
                        'labelEn': 'Kiribati',
                        'labels': [
                            {
                                'label': 'Kiribati',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KIR'
                    },
                    {
                        'labelEn': 'Saint Kitts and Nevis',
                        'labels': [
                            {
                                'label': 'Saint Kitts and Nevis',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KNA'
                    },
                    {
                        'labelEn': 'South Korea',
                        'labels': [
                            {
                                'label': 'South Korea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KOR'
                    },
                    {
                        'labelEn': 'Kuwait',
                        'labels': [
                            {
                                'label': 'Kuwait',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KWT'
                    },
                    {
                        'labelEn': "Lao People's Democratic Republic",
                        'labels': [
                            {
                                'label': "Lao People's Democratic Republic",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LAO'
                    },
                    {
                        'labelEn': 'Lebanon',
                        'labels': [
                            {
                                'label': 'Lebanon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LBN'
                    },
                    {
                        'labelEn': 'Liberia',
                        'labels': [
                            {
                                'label': 'Liberia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LBR'
                    },
                    {
                        'labelEn': 'Libya',
                        'labels': [
                            {
                                'label': 'Libya',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LBY'
                    },
                    {
                        'labelEn': 'Saint Lucia',
                        'labels': [
                            {
                                'label': 'Saint Lucia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LCA'
                    },
                    {
                        'labelEn': 'Liechtenstein',
                        'labels': [
                            {
                                'label': 'Liechtenstein',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LIE'
                    },
                    {
                        'labelEn': 'Sri Lanka',
                        'labels': [
                            {
                                'label': 'Sri Lanka',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LKA'
                    },
                    {
                        'labelEn': 'Lesotho',
                        'labels': [
                            {
                                'label': 'Lesotho',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LSO'
                    },
                    {
                        'labelEn': 'Lithuania',
                        'labels': [
                            {
                                'label': 'Lithuania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LTU'
                    },
                    {
                        'labelEn': 'Luxembourg',
                        'labels': [
                            {
                                'label': 'Luxembourg',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LUX'
                    },
                    {
                        'labelEn': 'Latvia',
                        'labels': [
                            {
                                'label': 'Latvia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LVA'
                    },
                    {
                        'labelEn': 'Macao',
                        'labels': [
                            {
                                'label': 'Macao',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MAC'
                    },
                    {
                        'labelEn': 'Morocco',
                        'labels': [
                            {
                                'label': 'Morocco',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MAR'
                    },
                    {
                        'labelEn': 'Monaco',
                        'labels': [
                            {
                                'label': 'Monaco',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MCO'
                    },
                    {
                        'labelEn': 'Republic of Moldova',
                        'labels': [
                            {
                                'label': 'Republic of Moldova',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MDA'
                    },
                    {
                        'labelEn': 'Madagascar',
                        'labels': [
                            {
                                'label': 'Madagascar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MDG'
                    },
                    {
                        'labelEn': 'Maldives',
                        'labels': [
                            {
                                'label': 'Maldives',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MDV'
                    },
                    {
                        'labelEn': 'Mexico',
                        'labels': [
                            {
                                'label': 'Mexico',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MEX'
                    },
                    {
                        'labelEn': 'Marshall Islands',
                        'labels': [
                            {
                                'label': 'Marshall Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MHL'
                    },
                    {
                        'labelEn': 'Republic of North Macedonia',
                        'labels': [
                            {
                                'label': 'Republic of North Macedonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MKD'
                    },
                    {
                        'labelEn': 'Mali',
                        'labels': [
                            {
                                'label': 'Mali',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MLI'
                    },
                    {
                        'labelEn': 'Malta',
                        'labels': [
                            {
                                'label': 'Malta',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MLT'
                    },
                    {
                        'labelEn': 'Myanmar',
                        'labels': [
                            {
                                'label': 'Myanmar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MMR'
                    },
                    {
                        'labelEn': 'Montenegro',
                        'labels': [
                            {
                                'label': 'Montenegro',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MNE'
                    },
                    {
                        'labelEn': 'Mongolia',
                        'labels': [
                            {
                                'label': 'Mongolia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MNG'
                    },
                    {
                        'labelEn': 'Northern Mariana Islands',
                        'labels': [
                            {
                                'label': 'Northern Mariana Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MNP'
                    },
                    {
                        'labelEn': 'Mozambique',
                        'labels': [
                            {
                                'label': 'Mozambique',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MOZ'
                    },
                    {
                        'labelEn': 'Mauritania',
                        'labels': [
                            {
                                'label': 'Mauritania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MRT'
                    },
                    {
                        'labelEn': 'Montserrat',
                        'labels': [
                            {
                                'label': 'Montserrat',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MSR'
                    },
                    {
                        'labelEn': 'Martinique',
                        'labels': [
                            {
                                'label': 'Martinique',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MTQ'
                    },
                    {
                        'labelEn': 'Mauritius',
                        'labels': [
                            {
                                'label': 'Mauritius',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MUS'
                    },
                    {
                        'labelEn': 'Malawi',
                        'labels': [
                            {
                                'label': 'Malawi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MWI'
                    },
                    {
                        'labelEn': 'Malaysia',
                        'labels': [
                            {
                                'label': 'Malaysia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MYS'
                    },
                    {
                        'labelEn': 'Mayotte',
                        'labels': [
                            {
                                'label': 'Mayotte',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MYT'
                    },
                    {
                        'labelEn': 'Namibia',
                        'labels': [
                            {
                                'label': 'Namibia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NAM'
                    },
                    {
                        'labelEn': 'New Caledonia',
                        'labels': [
                            {
                                'label': 'New Caledonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NCL'
                    },
                    {
                        'labelEn': 'Niger',
                        'labels': [
                            {
                                'label': 'Niger',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NER'
                    },
                    {
                        'labelEn': 'Norfolk Island',
                        'labels': [
                            {
                                'label': 'Norfolk Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NFK'
                    },
                    {
                        'labelEn': 'Nigeria',
                        'labels': [
                            {
                                'label': 'Nigeria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NGA'
                    },
                    {
                        'labelEn': 'Nicaragua',
                        'labels': [
                            {
                                'label': 'Nicaragua',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NIC'
                    },
                    {
                        'labelEn': 'Niue',
                        'labels': [
                            {
                                'label': 'Niue',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NIU'
                    },
                    {
                        'labelEn': 'Netherlands',
                        'labels': [
                            {
                                'label': 'Netherlands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NLD'
                    },
                    {
                        'labelEn': 'Norway',
                        'labels': [
                            {
                                'label': 'Norway',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NOR'
                    },
                    {
                        'labelEn': 'Nepal',
                        'labels': [
                            {
                                'label': 'Nepal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NPL'
                    },
                    {
                        'labelEn': 'Nauru',
                        'labels': [
                            {
                                'label': 'Nauru',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NRU'
                    },
                    {
                        'labelEn': 'New Zealand',
                        'labels': [
                            {
                                'label': 'New Zealand',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NZL'
                    },
                    {
                        'labelEn': 'Oman',
                        'labels': [
                            {
                                'label': 'Oman',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'OMN'
                    },
                    {
                        'labelEn': 'Pakistan',
                        'labels': [
                            {
                                'label': 'Pakistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PAK'
                    },
                    {
                        'labelEn': 'Panama',
                        'labels': [
                            {
                                'label': 'Panama',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PAN'
                    },
                    {
                        'labelEn': 'Pitcairn',
                        'labels': [
                            {
                                'label': 'Pitcairn',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PCN'
                    },
                    {
                        'labelEn': 'Peru',
                        'labels': [
                            {
                                'label': 'Peru',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PER'
                    },
                    {
                        'labelEn': 'Philippines',
                        'labels': [
                            {
                                'label': 'Philippines',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PHL'
                    },
                    {
                        'labelEn': 'Palau',
                        'labels': [
                            {
                                'label': 'Palau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PLW'
                    },
                    {
                        'labelEn': 'Papua New Guinea',
                        'labels': [
                            {
                                'label': 'Papua New Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PNG'
                    },
                    {
                        'labelEn': 'Poland',
                        'labels': [
                            {
                                'label': 'Poland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'POL'
                    },
                    {
                        'labelEn': 'Puerto Rico',
                        'labels': [
                            {
                                'label': 'Puerto Rico',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRI'
                    },
                    {
                        'labelEn': "Democratic People's Republic of Korea",
                        'labels': [
                            {
                                'label': "Democratic People's Republic of Korea",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRK'
                    },
                    {
                        'labelEn': 'Portugal',
                        'labels': [
                            {
                                'label': 'Portugal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRT'
                    },
                    {
                        'labelEn': 'Paraguay',
                        'labels': [
                            {
                                'label': 'Paraguay',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRY'
                    },
                    {
                        'labelEn': 'Palestinian Territory, Occupied',
                        'labels': [
                            {
                                'label': 'Palestinian Territory, Occupied',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PSE'
                    },
                    {
                        'labelEn': 'French Polynesia',
                        'labels': [
                            {
                                'label': 'French Polynesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PYF'
                    },
                    {
                        'labelEn': 'Qatar',
                        'labels': [
                            {
                                'label': 'Qatar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'QAT'
                    },
                    {
                        'labelEn': 'Réunion',
                        'labels': [
                            {
                                'label': 'Réunion',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'REU'
                    },
                    {
                        'labelEn': 'Romania',
                        'labels': [
                            {
                                'label': 'Romania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ROU'
                    },
                    {
                        'labelEn': 'Russia',
                        'labels': [
                            {
                                'label': 'Russia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RUS'
                    },
                    {
                        'labelEn': 'Rwanda',
                        'labels': [
                            {
                                'label': 'Rwanda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RWA'
                    },
                    {
                        'labelEn': 'Saudi Arabia',
                        'labels': [
                            {
                                'label': 'Saudi Arabia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SAU'
                    },
                    {
                        'labelEn': 'Sudan',
                        'labels': [
                            {
                                'label': 'Sudan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SDN'
                    },
                    {
                        'labelEn': 'Senegal',
                        'labels': [
                            {
                                'label': 'Senegal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SEN'
                    },
                    {
                        'labelEn': 'Singapore',
                        'labels': [
                            {
                                'label': 'Singapore',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SGP'
                    },
                    {
                        'labelEn': 'South Georgia and the South Sandwich Islands',
                        'labels': [
                            {
                                'label': 'South Georgia and the South Sandwich Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SGS'
                    },
                    {
                        'labelEn': 'Saint Helena, Ascension and Tristan da Cunha',
                        'labels': [
                            {
                                'label': 'Saint Helena, Ascension and Tristan da Cunha',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SHN'
                    },
                    {
                        'labelEn': 'Svalbard and Jan Mayen',
                        'labels': [
                            {
                                'label': 'Svalbard and Jan Mayen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SJM'
                    },
                    {
                        'labelEn': 'Solomon Islands',
                        'labels': [
                            {
                                'label': 'Solomon Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SLB'
                    },
                    {
                        'labelEn': 'Sierra Leone',
                        'labels': [
                            {
                                'label': 'Sierra Leone',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SLE'
                    },
                    {
                        'labelEn': 'El Salvador',
                        'labels': [
                            {
                                'label': 'El Salvador',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SLV'
                    },
                    {
                        'labelEn': 'San Marino',
                        'labels': [
                            {
                                'label': 'San Marino',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SMR'
                    },
                    {
                        'labelEn': 'Somalia',
                        'labels': [
                            {
                                'label': 'Somalia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SOM'
                    },
                    {
                        'labelEn': 'Saint Pierre and Miquelon',
                        'labels': [
                            {
                                'label': 'Saint Pierre and Miquelon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SPM'
                    },
                    {
                        'labelEn': 'Serbia',
                        'labels': [
                            {
                                'label': 'Serbia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SRB'
                    },
                    {
                        'labelEn': 'South Sudan',
                        'labels': [
                            {
                                'label': 'South Sudan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SSD'
                    },
                    {
                        'labelEn': 'Sao Tome and Principe',
                        'labels': [
                            {
                                'label': 'Sao Tome and Principe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'STP'
                    },
                    {
                        'labelEn': 'Suriname',
                        'labels': [
                            {
                                'label': 'Suriname',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SUR'
                    },
                    {
                        'labelEn': 'Slovakia',
                        'labels': [
                            {
                                'label': 'Slovakia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SVK'
                    },
                    {
                        'labelEn': 'Slovenia',
                        'labels': [
                            {
                                'label': 'Slovenia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SVN'
                    },
                    {
                        'labelEn': 'Sweden',
                        'labels': [
                            {
                                'label': 'Sweden',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SWE'
                    },
                    {
                        'labelEn': 'Swaziland',
                        'labels': [
                            {
                                'label': 'Swaziland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SWZ'
                    },
                    {
                        'labelEn': 'Seychelles',
                        'labels': [
                            {
                                'label': 'Seychelles',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SYC'
                    },
                    {
                        'labelEn': 'Syrian Arab Republic',
                        'labels': [
                            {
                                'label': 'Syrian Arab Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SYR'
                    },
                    {
                        'labelEn': 'Turks and Caicos Islands',
                        'labels': [
                            {
                                'label': 'Turks and Caicos Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TCA'
                    },
                    {
                        'labelEn': 'Chad',
                        'labels': [
                            {
                                'label': 'Chad',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TCD'
                    },
                    {
                        'labelEn': 'Togo',
                        'labels': [
                            {
                                'label': 'Togo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TGO'
                    },
                    {
                        'labelEn': 'Thailand',
                        'labels': [
                            {
                                'label': 'Thailand',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'THA'
                    },
                    {
                        'labelEn': 'Tajikistan',
                        'labels': [
                            {
                                'label': 'Tajikistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TJK'
                    },
                    {
                        'labelEn': 'Tokelau',
                        'labels': [
                            {
                                'label': 'Tokelau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TKL'
                    },
                    {
                        'labelEn': 'Turkmenistan',
                        'labels': [
                            {
                                'label': 'Turkmenistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TKM'
                    },
                    {
                        'labelEn': 'Timor-Leste',
                        'labels': [
                            {
                                'label': 'Timor-Leste',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TLS'
                    },
                    {
                        'labelEn': 'Tonga',
                        'labels': [
                            {
                                'label': 'Tonga',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TON'
                    },
                    {
                        'labelEn': 'Trinidad and Tobago',
                        'labels': [
                            {
                                'label': 'Trinidad and Tobago',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TTO'
                    },
                    {
                        'labelEn': 'Tunisia',
                        'labels': [
                            {
                                'label': 'Tunisia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TUN'
                    },
                    {
                        'labelEn': 'Turkey',
                        'labels': [
                            {
                                'label': 'Turkey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TUR'
                    },
                    {
                        'labelEn': 'Tuvalu',
                        'labels': [
                            {
                                'label': 'Tuvalu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TUV'
                    },
                    {
                        'labelEn': 'Taiwan',
                        'labels': [
                            {
                                'label': 'Taiwan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TWN'
                    },
                    {
                        'labelEn': 'Tanzania, United Republic of',
                        'labels': [
                            {
                                'label': 'Tanzania, United Republic of',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TZA'
                    },
                    {
                        'labelEn': 'Uganda',
                        'labels': [
                            {
                                'label': 'Uganda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UGA'
                    },
                    {
                        'labelEn': 'Ukraine',
                        'labels': [
                            {
                                'label': 'Ukraine',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UKR'
                    },
                    {
                        'labelEn': 'United States Minor Outlying Islands',
                        'labels': [
                            {
                                'label': 'United States Minor Outlying Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UMI'
                    },
                    {
                        'labelEn': 'Uruguay',
                        'labels': [
                            {
                                'label': 'Uruguay',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'URY'
                    },
                    {
                        'labelEn': 'United States',
                        'labels': [
                            {
                                'label': 'United States',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'USA'
                    },
                    {
                        'labelEn': 'Uzbekistan',
                        'labels': [
                            {
                                'label': 'Uzbekistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UZB'
                    },
                    {
                        'labelEn': 'Holy See (Vatican City State)',
                        'labels': [
                            {
                                'label': 'Holy See (Vatican City State)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VAT'
                    },
                    {
                        'labelEn': 'Saint Vincent and the Grenadines',
                        'labels': [
                            {
                                'label': 'Saint Vincent and the Grenadines',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VCT'
                    },
                    {
                        'labelEn': 'Venezuela',
                        'labels': [
                            {
                                'label': 'Venezuela',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VEN'
                    },
                    {
                        'labelEn': 'Virgin Islands, British',
                        'labels': [
                            {
                                'label': 'Virgin Islands, British',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VGB'
                    },
                    {
                        'labelEn': 'Virgin Islands, U.S.',
                        'labels': [
                            {
                                'label': 'Virgin Islands, U.S.',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VIR'
                    },
                    {
                        'labelEn': 'Vietnam',
                        'labels': [
                            {
                                'label': 'Vietnam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VNM'
                    },
                    {
                        'labelEn': 'Vanuatu',
                        'labels': [
                            {
                                'label': 'Vanuatu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VUT'
                    },
                    {
                        'labelEn': 'Wallis and Futuna',
                        'labels': [
                            {
                                'label': 'Wallis and Futuna',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WLF'
                    },
                    {
                        'labelEn': 'Samoa',
                        'labels': [
                            {
                                'label': 'Samoa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WSM'
                    },
                    {
                        'labelEn': 'Yemen',
                        'labels': [
                            {
                                'label': 'Yemen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'YEM'
                    },
                    {
                        'labelEn': 'South Africa',
                        'labels': [
                            {
                                'label': 'South Africa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZAF'
                    },
                    {
                        'labelEn': 'Zambia',
                        'labels': [
                            {
                                'label': 'Zambia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZMB'
                    },
                    {
                        'labelEn': 'Zimbabwe',
                        'labels': [
                            {
                                'label': 'Zimbabwe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZWE'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Country',
                'labels': [
                    {
                        'label': 'Country',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'country',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Address',
                'labels': [
                    {
                        'label': 'Address',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'address',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Household resides in (Select administrative level 1)',
                'labels': [
                    {
                        'label': 'Household resides in (Select administrative level 1)',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'admin1',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Household resides in (Select administrative level 2)',
                'labels': [
                    {
                        'label': 'Household resides in (Select administrative level 2)',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'admin2',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'UNHCR Case ID',
                'labels': [
                    {
                        'label': 'UNHCR Case ID',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'unhcr_id',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'What is the household size?',
                'labels': [
                    {
                        'label': 'What is the household size?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'size',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Aunt / Uncle',
                        'labels': [
                            {
                                'label': 'Aunt / Uncle',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AUNT_UNCLE'
                    },
                    {
                        'labelEn': 'Brother / Sister',
                        'labels': [
                            {
                                'label': 'Brother / Sister',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BROTHER_SISTER'
                    },
                    {
                        'labelEn': 'Cousin',
                        'labels': [
                            {
                                'label': 'Cousin',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COUSIN'
                    },
                    {
                        'labelEn': 'Daughter-in-law / Son-in-law',
                        'labels': [
                            {
                                'label': 'Daughter-in-law / Son-in-law',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DAUGHTERINLAW_SONINLAW'
                    },
                    {
                        'labelEn': 'Granddaughter / Grandson',
                        'labels': [
                            {
                                'label': 'Granddaughter / Grandson',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GRANDDAUGHER_GRANDSON'
                    },
                    {
                        'labelEn': 'Grandmother / Grandfather',
                        'labels': [
                            {
                                'label': 'Grandmother / Grandfather',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GRANDMOTHER_GRANDFATHER'
                    },
                    {
                        'labelEn': 'Head of household (self)',
                        'labels': [
                            {
                                'label': 'Head of household (self)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HEAD'
                    },
                    {
                        'labelEn': 'Mother-in-law / Father-in-law',
                        'labels': [
                            {
                                'label': 'Mother-in-law / Father-in-law',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MOTHERINLAW_FATHERINLAW'
                    },
                    {
                        'labelEn': 'Mother / Father',
                        'labels': [
                            {
                                'label': 'Mother / Father',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MOTHER_FATHER'
                    },
                    {
                        'labelEn': 'Nephew / Niece',
                        'labels': [
                            {
                                'label': 'Nephew / Niece',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NEPHEW_NIECE'
                    },
                    {
                        'labelEn': 'Not a Family Member. Can only act as a recipient.',
                        'labels': [
                            {
                                'label': 'Not a Family Member. Can only act as a recipient.',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NON_BENEFICIARY'
                    },
                    {
                        'labelEn': 'Sister-in-law / Brother-in-law',
                        'labels': [
                            {
                                'label': 'Sister-in-law / Brother-in-law',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SISTERINLAW_BROTHERINLAW'
                    },
                    {
                        'labelEn': 'Son / Daughter',
                        'labels': [
                            {
                                'label': 'Son / Daughter',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SON_DAUGHTER'
                    },
                    {
                        'labelEn': 'Wife / Husband',
                        'labels': [
                            {
                                'label': 'Wife / Husband',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WIFE_HUSBAND'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Relationship to Head of Household',
                'labels': [
                    {
                        'label': 'Relationship to Head of Household',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'relationship',
                'required': True,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Full Name',
                'labels': [
                    {
                        'label': 'Full Name',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'full_name',
                'required': True,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Given Name',
                'labels': [
                    {
                        'label': 'Given Name',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'given_name',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Middle Names',
                'labels': [
                    {
                        'label': 'Middle Names',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'middle_name',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Family Name',
                'labels': [
                    {
                        'label': 'Family Name',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'family_name',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Female',
                        'labels': [
                            {
                                'label': 'Female',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FEMALE'
                    },
                    {
                        'labelEn': 'Male',
                        'labels': [
                            {
                                'label': 'Male',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MALE'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Gender',
                'labels': [
                    {
                        'label': 'Gender',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'sex',
                'required': True,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Divorced',
                        'labels': [
                            {
                                'label': 'Divorced',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DIVORCED'
                    },
                    {
                        'labelEn': 'Married',
                        'labels': [
                            {
                                'label': 'Married',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MARRIED'
                    },
                    {
                        'labelEn': 'Separated',
                        'labels': [
                            {
                                'label': 'Separated',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SEPARATED'
                    },
                    {
                        'labelEn': 'Single',
                        'labels': [
                            {
                                'label': 'Single',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SINGLE'
                    },
                    {
                        'labelEn': 'Widowed',
                        'labels': [
                            {
                                'label': 'Widowed',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WIDOWED'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Marital Status',
                'labels': [
                    {
                        'label': 'Marital Status',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'marital_status',
                'required': True,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Phone number',
                'labels': [
                    {
                        'label': 'Phone number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'phone_no',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Alternative phone number',
                'labels': [
                    {
                        'label': 'Alternative phone number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'phone_no_alternative',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Birth certificate number',
                'labels': [
                    {
                        'label': 'Birth certificate number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'birth_certificate_no',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': "Driver's license number",
                'labels': [
                    {
                        'label': "Driver's license number",
                        'language': 'English(EN)'
                    }
                ],
                'name': 'drivers_license_no',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Electoral card number',
                'labels': [
                    {
                        'label': 'Electoral card number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'electoral_card_no',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'UNHCR ID number',
                'labels': [
                    {
                        'label': 'UNHCR ID number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'unhcr_id_no',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'National passport number',
                'labels': [
                    {
                        'label': 'National passport number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'national_passport',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'National ID number',
                'labels': [
                    {
                        'label': 'National ID number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'national_id_no',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'WFP Scope ID number',
                'labels': [
                    {
                        'label': 'WFP Scope ID number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'scope_id_no',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'If other type of ID, specify the type',
                'labels': [
                    {
                        'label': 'If other type of ID, specify the type',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'other_id_type',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'ID number',
                'labels': [
                    {
                        'label': 'ID number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'other_id_no',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'How many pregnant women are there in the Household?',
                'labels': [
                    {
                        'label': 'How many pregnant women are there in the Household?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'pregnant_member',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females Age 0-5',
                'labels': [
                    {
                        'label': 'Females Age 0-5',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_0_5_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females Age 6-11',
                'labels': [
                    {
                        'label': 'Females Age 6-11',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_6_11_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females Age 12-17',
                'labels': [
                    {
                        'label': 'Females Age 12-17',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_12_17_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Female Adults',
                'labels': [
                    {
                        'label': 'Female Adults',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_adults_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Pregnant females',
                'labels': [
                    {
                        'label': 'Pregnant females',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'pregnant_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males Age 0-5',
                'labels': [
                    {
                        'label': 'Males Age 0-5',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_0_5_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males Age 6-11',
                'labels': [
                    {
                        'label': 'Males Age 6-11',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_6_11_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males Age 12-17',
                'labels': [
                    {
                        'label': 'Males Age 12-17',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_12_17_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Male Adults',
                'labels': [
                    {
                        'label': 'Male Adults',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_adults_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Female members with Disability age 0-5',
                'labels': [
                    {
                        'label': 'Female members with Disability age 0-5',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_0_5_disabled_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Female members with Disability age 6-11',
                'labels': [
                    {
                        'label': 'Female members with Disability age 6-11',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_6_11_disabled_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Female members with Disability age 12-17',
                'labels': [
                    {
                        'label': 'Female members with Disability age 12-17',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_12_17_disabled_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Female members with Disability adults',
                'labels': [
                    {
                        'label': 'Female members with Disability adults',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_adults_disabled_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Male members with Disability age 0-5',
                'labels': [
                    {
                        'label': 'Male members with Disability age 0-5',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_0_5_disabled_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Male members with Disability age 6-11',
                'labels': [
                    {
                        'label': 'Male members with Disability age 6-11',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_6_11_disabled_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Male members with Disability age 12-17',
                'labels': [
                    {
                        'label': 'Male members with Disability age 12-17',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_12_17_disabled_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Male members with Disability adults',
                'labels': [
                    {
                        'label': 'Male members with Disability adults',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_adults_disabled_count',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NO'
                    },
                    {
                        'labelEn': 'Not provided',
                        'labels': [
                            {
                                'label': 'Not provided',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NOT_PROVIDED'
                    },
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'YES'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Does the individual work?',
                'labels': [
                    {
                        'label': 'Does the individual work?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'work_status',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Difficulty communicating (e.g understanding or being understood)',
                        'labels': [
                            {
                                'label': 'Difficulty communicating (e.g understanding or being understood)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COMMUNICATING'
                    },
                    {
                        'labelEn': 'Difficulty hearing (even if using a hearing aid)',
                        'labels': [
                            {
                                'label': 'Difficulty hearing (even if using a hearing aid)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HEARING'
                    },
                    {
                        'labelEn': 'Difficulty remembering or concentrating',
                        'labels': [
                            {
                                'label': 'Difficulty remembering or concentrating',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MEMORY'
                    },
                    {
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NONE'
                    },
                    {
                        'labelEn': 'Difficulty seeing (even if wearing glasses)',
                        'labels': [
                            {
                                'label': 'Difficulty seeing (even if wearing glasses)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SEEING'
                    },
                    {
                        'labelEn': 'Difficulty with self care (washing, dressing)',
                        'labels': [
                            {
                                'label': 'Difficulty with self care (washing, dressing)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SELF_CARE'
                    },
                    {
                        'labelEn': 'Difficulty walking or climbing steps',
                        'labels': [
                            {
                                'label': 'Difficulty walking or climbing steps',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WALKING'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Does the individual have disability?',
                'labels': [
                    {
                        'label': 'Does the individual have disability?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'observed_disability',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CANNOT_DO'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LOT_DIFFICULTY'
                    },
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SOME_DIFFICULTY'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'If the individual has difficulty seeing, what is the severity?',
                'labels': [
                    {
                        'label': 'If the individual has difficulty seeing, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'seeing_disability',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CANNOT_DO'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LOT_DIFFICULTY'
                    },
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SOME_DIFFICULTY'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'If the individual has difficulty hearing, what is the severity?',
                'labels': [
                    {
                        'label': 'If the individual has difficulty hearing, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'hearing_disability',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CANNOT_DO'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LOT_DIFFICULTY'
                    },
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SOME_DIFFICULTY'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'If the individual has difficulty walking or climbing steps, what is the severity?',
                'labels': [
                    {
                        'label': 'If the individual has difficulty walking or climbing steps, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'physical_disability',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CANNOT_DO'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LOT_DIFFICULTY'
                    },
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SOME_DIFFICULTY'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'If the individual has difficulty remembering or concentrating, what is the severity?',
                'labels': [
                    {
                        'label': 'If the individual has difficulty remembering or concentrating, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'memory_disability',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CANNOT_DO'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LOT_DIFFICULTY'
                    },
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SOME_DIFFICULTY'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Do you have difficulty (with self-care such as) washing all over or dressing',
                'labels': [
                    {
                        'label': 'Do you have difficulty (with self-care such as) washing all over or dressing',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'selfcare_disability',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CANNOT_DO'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LOT_DIFFICULTY'
                    },
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SOME_DIFFICULTY'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'If the individual has difficulty communicating, what is the severity?',
                'labels': [
                    {
                        'label': 'If the individual has difficulty communicating, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'comms_disability',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Village',
                'labels': [
                    {
                        'label': 'Village',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'village',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Data collection start date',
                'labels': [
                    {
                        'label': 'Data collection start date',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'start',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Data collection end date',
                'labels': [
                    {
                        'label': 'Data collection end date',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'end',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Device ID',
                'labels': [
                    {
                        'label': 'Device ID',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'deviceid',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Name of the enumerator',
                'labels': [
                    {
                        'label': 'Name of the enumerator',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'name_enumerator',
                'required': True,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Partner',
                        'labels': [
                            {
                                'label': 'Partner',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PARTNER'
                    },
                    {
                        'labelEn': 'UNICEF',
                        'labels': [
                            {
                                'label': 'UNICEF',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UNICEF'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Organization of the enumerator',
                'labels': [
                    {
                        'label': 'Organization of the enumerator',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'org_enumerator',
                'required': True,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Government partners',
                        'labels': [
                            {
                                'label': 'Government partners',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GOVERNMENT_PARTNER'
                    },
                    {
                        'labelEn': 'Humanitarian partners',
                        'labels': [
                            {
                                'label': 'Humanitarian partners',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HUMANITARIAN_PARTNER'
                    },
                    {
                        'labelEn': 'Private partners',
                        'labels': [
                            {
                                'label': 'Private partners',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRIVATE_PARTNER'
                    },
                    {
                        'labelEn': 'UNICEF',
                        'labels': [
                            {
                                'label': 'UNICEF',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UNICEF'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Which organizations may we share your information with?',
                'labels': [
                    {
                        'label': 'Which organizations may we share your information with?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'consent_sharing',
                'required': True,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Name of partner organization',
                'labels': [
                    {
                        'label': 'Name of partner organization',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'org_name_enumerator',
                'required': True,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Who answers this phone?',
                'labels': [
                    {
                        'label': 'Who answers this phone?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'who_answers_phone',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Who answers this phone?',
                'labels': [
                    {
                        'label': 'Who answers this phone?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'who_answers_alt_phone',
                'required': False,
                'type': 'STRING'
            }
        ]
    }
}
