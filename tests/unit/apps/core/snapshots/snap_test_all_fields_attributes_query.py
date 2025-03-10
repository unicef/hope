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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
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
                'name': 'coping_strategy_neg_job_h_f',
                'required': False,
                'type': 'SELECT_ONE'
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Age at registration',
                'labels': [
                    {
                        'label': 'Age at registration',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'age_at_registration',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Any other source?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Any other source?',
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
                        'value': '0'
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
                        'value': '1'
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
                'labelEn': 'Are there any drug addicts in the family?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Are there any drug addicts in the family?',
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
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'primary',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'primary',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'primary'
                    },
                    {
                        'labelEn': 'secondary',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'secondary',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'secondary'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'At what level is the child attending?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'At what level is the child attending?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'school_level_i_f',
                'required': False,
                'type': 'SELECT_ONE'
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
                'labelEn': 'Birth date',
                'labels': [
                    {
                        'label': 'Birth date',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'birth_date',
                'required': True,
                'type': 'DATE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Borrow food or rely on help from friends or relatives',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Borrow food or rely on help from friends or relatives',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'red_coping_strategy_borrow_food_h_f',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Borrowed Money',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Borrowed Money',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_borrow_h_f',
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
                        'value': '0'
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
                        'value': '1'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Can you meet the basic needs of your household according to your priorities?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Can you meet the basic needs of your household according to your priorities?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'meet_household_needs_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Cash transfer from an NGO, CBOs , or religious organization',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Cash transfer from an NGO, CBOs , or religious organization',
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
                'labelEn': 'Cash transfer from government',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Cash transfer from government',
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
                        'value': '0'
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
                        'value': '1'
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
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
                'name': 'coping_strategy_change_housing_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Child headed Household',
                'labels': [
                    {
                        'label': 'Child headed Household',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'child_hoh',
                'required': False,
                'type': 'BOOL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Child is Head of Household',
                'labels': [
                    {
                        'label': 'Child is Head of Household',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'child_hoh',
                'required': False,
                'type': 'BOOL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Child is female and Head of Household',
                'labels': [
                    {
                        'label': 'Child is female and Head of Household',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'fchild_hoh',
                'required': False,
                'type': 'BOOL'
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Consumed seed stocks that were to be held/saved for next season',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Consumed seed stocks that were to be held/saved for next season',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_consume_seed_h_f',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Consumed wild food',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': 'Consommé des aliments sauvages',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Consumed wild food',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_wild_food_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': 'country origin',
                'isFlexField': False,
                'labelEn': 'Country of Origin',
                'labels': [
                    {
                        'label': 'Country of Origin',
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
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Country of registration',
                'labels': [
                    {
                        'label': 'Country of registration',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'country',
                'required': True,
                'type': 'SELECT_ONE'
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
                        'value': '0'
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
                        'value': '1'
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
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Do you consent?',
                'labels': [
                    {
                        'label': 'Do you consent?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'consent',
                'required': False,
                'type': 'BOOL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
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
                        'value': '0'
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
                        'value': '1'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Do you have odor, taste or color in the water?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Do you have odor, taste or color in the water?',
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
                        'labelEn': 'Yes - Bags',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes - Bags',
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
                        'labelEn': 'Yes - Bins',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes - Bins',
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
                        'labelEn': 'Difficulty walking or climbing steps',
                        'labels': [
                            {
                                'label': 'Difficulty walking or climbing steps',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WALKING'
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NONE'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Does the Individual have disability?',
                'labels': [
                    {
                        'label': 'Does the Individual have disability?',
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
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '0'
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
                        'value': '1'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Does the Individual have paid employment in the current month?',
                'labels': [
                    {
                        'label': 'Does the Individual have paid employment in the current month?',
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
                        'value': '0'
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
                        'value': '1'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Does the child participate in a nutritional programme?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': "L'enfant participe-t-il a un traitement nutritionnel?",
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Does the child participate in a nutritional programme?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'mas_treatment_i_f',
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
                        'value': '0'
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
                        'value': '1'
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
                        'value': '0'
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
                        'value': '1'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Does your latrine have a door, light and ventilation?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Does your latrine have a door, light and ventilation?',
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
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Domestic service job in someone else’s house',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Domestic service job in someone else’s house',
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
                        'value': '0'
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
                        'value': '1'
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
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'End of service payment',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'End of service payment',
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Estimated birth date?',
                'labels': [
                    {
                        'label': 'Estimated birth date?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'estimated_birth_date',
                'required': True,
                'type': 'BOOL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Female child headed Household',
                'labels': [
                    {
                        'label': 'Female child headed Household',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'fchild_hoh',
                'required': False,
                'type': 'BOOL'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Female members with Disability age 60 +',
                'labels': [
                    {
                        'label': 'Female members with Disability age 60 +',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_60_disabled_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females Age 0 - 5',
                'labels': [
                    {
                        'label': 'Females Age 0 - 5',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_0_5_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females Age 12 - 17',
                'labels': [
                    {
                        'label': 'Females Age 12 - 17',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_12_17_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females Age 18 - 59',
                'labels': [
                    {
                        'label': 'Females Age 18 - 59',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_18_59_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females Age 18 - 59 with disability',
                'labels': [
                    {
                        'label': 'Females Age 18 - 59 with disability',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_18_59_disabled_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females Age 6 - 11',
                'labels': [
                    {
                        'label': 'Females Age 6 - 11',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_6_11_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females Age 60 +',
                'labels': [
                    {
                        'label': 'Females Age 60 +',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_60_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females age 0 - 5 with disability',
                'labels': [
                    {
                        'label': 'Females age 0 - 5 with disability',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_0_5_disabled_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females age 12 - 17 with disability',
                'labels': [
                    {
                        'label': 'Females age 12 - 17 with disability',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_12_17_disabled_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Females age 6 - 11 with disability',
                'labels': [
                    {
                        'label': 'Females age 6 - 11 with disability',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'female_age_group_6_11_disabled_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'First Household registration date',
                'labels': [
                    {
                        'label': 'First Household registration date',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'first_registration_date',
                'required': True,
                'type': 'DATE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'First Individual registration date',
                'labels': [
                    {
                        'label': 'First Individual registration date',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'first_registration_date',
                'required': True,
                'type': 'DATE'
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
                        'value': '0'
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
                        'value': '1'
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
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'For what reasons (i.e. to meet which essential needs) did you (or other members in your household) adopt such coping strategy(ies)?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'For what reasons (i.e. to meet which essential needs) did you (or other members in your household) adopt such coping strategy(ies)?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_reason_h_f',
                'required': False,
                'type': 'STRING'
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
                        'value': '0'
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
                        'value': '1'
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
                    },
                    {
                        'labelEn': 'Not answered',
                        'labels': [
                            {
                                'label': 'Not answered',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NOT_ANSWERED'
                    },
                    {
                        'labelEn': 'Not collected',
                        'labels': [
                            {
                                'label': 'Not collected',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NOT_COLLECTED'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'OTHER'
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
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Gender group with other sex',
                'labels': [
                    {
                        'label': 'Gender group with other sex',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'other_sex_group_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Gender group with unknown sex',
                'labels': [
                    {
                        'label': 'Gender group with unknown sex',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'unknown_sex_group_count',
                'required': False,
                'type': 'INTEGER'
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
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Gift from family/friend/other person',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Gift from family/friend/other person',
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
                        'value': '0'
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
                        'value': '1'
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
                        'value': '0'
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
                        'value': '1'
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
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Has phone number?',
                'labels': [
                    {
                        'label': 'Has phone number?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'has_phone_number',
                'required': False,
                'type': 'BOOL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Has tax ID number?',
                'labels': [
                    {
                        'label': 'Has tax ID number?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'has_tax_id_number',
                'required': False,
                'type': 'BOOL'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Has the bank account number?',
                'labels': [
                    {
                        'label': 'Has the bank account number?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'has_the_bank_account_number',
                'required': False,
                'type': 'BOOL'
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
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Household resides in which admin1?',
                'labels': [
                    {
                        'label': 'Household resides in which admin1?',
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
                'labelEn': 'Household resides in which admin2?',
                'labels': [
                    {
                        'label': 'Household resides in which admin2?',
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
                'labelEn': 'Household resides in which admin3?',
                'labels': [
                    {
                        'label': 'Household resides in which admin3?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'admin3',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Household resides in which admin4?',
                'labels': [
                    {
                        'label': 'Household resides in which admin4?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'admin4',
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How many children did ${full_name_i_c} have in total, including those who do not reside in the household and / or those who died.',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': 'Combien d’enfants le collecteur a-t-il eu au total, incluant ceux qui ne resident pas dans le ménage et/ou ceux qui sont décédés.',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many children did ${full_name_i_c} have in total, including those who do not reside in the household and / or those who died.',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'verif_primary_children_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How many children of ${full_name_i_c} are currently in primary school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': 'Combien d’enfants du collecteur sont actuellement à l’école primaire\xa0?',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many children of ${full_name_i_c} are currently in primary school?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'verif_primary_children_school_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': "How many closed rooms are there in ${full_name_i_c} 's house?",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': 'Combien de pièces fermées y a-t-il dans la maison du collecteur?',
                        'language': 'French(FR)'
                    },
                    {
                        'label': "How many closed rooms are there in ${full_name_i_c} 's house?",
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'verif_primary_rooms_house_i_f',
                'required': False,
                'type': 'INTEGER'
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
                    {
                        'labelEn': 'At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '0'
                    },
                    {
                        'labelEn': 'Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
                    },
                    {
                        'labelEn': 'More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3'
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
                        'value': '4'
                    },
                    {
                        'labelEn': 'All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'I have felt active and vigorous',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'I have felt active and vigorous',
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
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '0'
                    },
                    {
                        'labelEn': 'Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
                    },
                    {
                        'labelEn': 'More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3'
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
                        'value': '4'
                    },
                    {
                        'labelEn': 'All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'I have felt cheerful and in good spirits',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'I have felt cheerful and in good spirits',
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
                        'labelEn': 'At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '0'
                    },
                    {
                        'labelEn': 'Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
                    },
                    {
                        'labelEn': 'More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3'
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
                        'value': '4'
                    },
                    {
                        'labelEn': 'All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'I have felt relaxed and calm',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'I have felt relaxed and calm',
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
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '0'
                    },
                    {
                        'labelEn': 'Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
                    },
                    {
                        'labelEn': 'More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3'
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
                        'value': '4'
                    },
                    {
                        'labelEn': 'All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'I woke up feeling fresh and rested',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'I woke up feeling fresh and rested',
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
                        'value': '0'
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
                        'value': '1'
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
                        'value': '0'
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
                        'value': '1'
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If one or both have passed away, what is the reason of their death?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If one or both have passed away, what is the reason of their death?',
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
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If other, please specify',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If other, please specify',
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
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
                'labelEn': 'If the Individual has difficulty communicating, what is the severity?',
                'labels': [
                    {
                        'label': 'If the Individual has difficulty communicating, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'comms_disability',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
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
                'labelEn': 'If the Individual has difficulty hearing, what is the severity?',
                'labels': [
                    {
                        'label': 'If the Individual has difficulty hearing, what is the severity?',
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
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
                'labelEn': 'If the Individual has difficulty remembering or concentrating, what is the severity?',
                'labels': [
                    {
                        'label': 'If the Individual has difficulty remembering or concentrating, what is the severity?',
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
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
                'labelEn': 'If the Individual has difficulty seeing, what is the severity?',
                'labels': [
                    {
                        'label': 'If the Individual has difficulty seeing, what is the severity?',
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
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
                'labelEn': 'If the Individual has difficulty walking or climbing steps, what is the severity?',
                'labels': [
                    {
                        'label': 'If the Individual has difficulty walking or climbing steps, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'physical_disability',
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
                        'value': '0'
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
                        'value': '1'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If the individual is a child, does he/she currently enrolled in school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If the individual is a child, does he/she currently enrolled in school?',
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
                        'value': '0'
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
                        'value': '1'
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
                        'value': '0'
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
                        'value': '1'
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
                        'value': '0'
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
                        'value': '1'
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
                'labelEn': 'Income (or goods) from household enterprise (profit or otherwise)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Income (or goods) from household enterprise (profit or otherwise)',
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
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'disabled',
                        'labels': [
                            {
                                'label': 'disabled',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'disabled'
                    },
                    {
                        'labelEn': 'not disabled',
                        'labels': [
                            {
                                'label': 'not disabled',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'not disabled'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Individual is disabled?',
                'labels': [
                    {
                        'label': 'Individual is disabled?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'disability',
                'required': False,
                'type': 'SELECT_ONE'
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
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Is the Individual pregnant?',
                'labels': [
                    {
                        'label': 'Is the Individual pregnant?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'pregnant',
                'required': False,
                'type': 'BOOL'
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
                        'value': '0'
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
                        'value': '1'
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
                        'value': '0'
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
                        'value': '1'
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
                        'value': '0'
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
                        'value': '1'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Is the spouse present dureing the current registration',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': "Est ce que le conjoint du collecteur est présent lors de l'enregistrement?",
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Is the spouse present dureing the current registration',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'spouse_present_primary_i_f',
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
                        'value': '0'
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
                        'value': '1'
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
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Is this a returnee Household?',
                'labels': [
                    {
                        'label': 'Is this a returnee Household?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'returnee',
                'required': False,
                'type': 'BOOL'
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Issuing country of birth certificate',
                'labels': [
                    {
                        'label': 'Issuing country of birth certificate',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'birth_certificate_issuer',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': "Issuing country of driver's license",
                'labels': [
                    {
                        'label': "Issuing country of driver's license",
                        'language': 'English(EN)'
                    }
                ],
                'name': 'drivers_license_issuer',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Issuing country of electoral card',
                'labels': [
                    {
                        'label': 'Issuing country of electoral card',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'electoral_card_issuer',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Issuing country of national ID',
                'labels': [
                    {
                        'label': 'Issuing country of national ID',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'national_id_issuer',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Issuing country of national passport',
                'labels': [
                    {
                        'label': 'Issuing country of national passport',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'national_passport_issuer',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Issuing country of other ID',
                'labels': [
                    {
                        'label': 'Issuing country of other ID',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'other_id_issuer',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Issuing entity of SCOPE ID',
                'labels': [
                    {
                        'label': 'Issuing entity of SCOPE ID',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'scope_id_issuer',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Issuing entity of UNHCR ID',
                'labels': [
                    {
                        'label': 'Issuing entity of UNHCR ID',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'unhcr_id_issuer',
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
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Limit portion size at mealtime',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Limit portion size at mealtime',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'red_coping_strategy_portion_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Loan (bank, other financial institution or organization)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Loan (bank, other financial institution or organization)',
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
                'labelEn': 'Loan (family, friend)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Loan (family, friend)',
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
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Male members with Disability age 60 +',
                'labels': [
                    {
                        'label': 'Male members with Disability age 60 +',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_60_disabled_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males Age 0 - 5',
                'labels': [
                    {
                        'label': 'Males Age 0 - 5',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_0_5_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males Age 12 - 17',
                'labels': [
                    {
                        'label': 'Males Age 12 - 17',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_12_17_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males Age 18 - 59',
                'labels': [
                    {
                        'label': 'Males Age 18 - 59',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_18_59_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males Age 18 - 59 with disability',
                'labels': [
                    {
                        'label': 'Males Age 18 - 59 with disability',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_18_59_disabled_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males Age 6 - 11',
                'labels': [
                    {
                        'label': 'Males Age 6 - 11',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_6_11_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males Age 60 +',
                'labels': [
                    {
                        'label': 'Males Age 60 +',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_60_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males age 0 - 5 with disability',
                'labels': [
                    {
                        'label': 'Males age 0 - 5 with disability',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_0_5_disabled_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males age 12 - 17 with disability',
                'labels': [
                    {
                        'label': 'Males age 12 - 17 with disability',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_12_17_disabled_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Males age 6 - 11 with disability',
                'labels': [
                    {
                        'label': 'Males age 6 - 11 with disability',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'male_age_group_6_11_disabled_count',
                'required': False,
                'type': 'INTEGER'
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
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
                'labelEn': 'Marital status',
                'labels': [
                    {
                        'label': 'Marital status',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'marital_status',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Married Child for financial purposes',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Married Child for financial purposes',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_child_marriage_h_f',
                'required': False,
                'type': 'SELECT_ONE'
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
                        'value': '0'
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
                        'value': '1'
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
                        'labelEn': 'Community-level Registration',
                        'labels': [
                            {
                                'label': 'Community-level Registration',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COMMUNITY'
                    },
                    {
                        'labelEn': 'Household Registration',
                        'labels': [
                            {
                                'label': 'Household Registration',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HH_REGISTRATION'
                    },
                    {
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Method of collection (e.g. HH survey, Community, etc.)',
                'labels': [
                    {
                        'label': 'Method of collection (e.g. HH survey, Community, etc.)',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'registration_method',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Micro-credit',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Micro-credit',
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
                        'value': '0'
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
                        'value': '1'
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
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'At no time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'At no time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '0'
                    },
                    {
                        'labelEn': 'Some of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'Less than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Less than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
                    },
                    {
                        'labelEn': 'More than half of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'More than half of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '3'
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
                        'value': '4'
                    },
                    {
                        'labelEn': 'All of the time',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'All of the time',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '5'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'My daily life has been filled with things that interest me',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'My daily life has been filled with things that interest me',
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
                'required': False,
                'type': 'STRING'
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
                'hint': "{'English(EN)': 'Count the number of 5 litre or more saucepans as 1 piece.'}",
                'isFlexField': True,
                'labelEn': 'Number of Cooking pots',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of Cooking pots',
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
                ],
                'hint': "{'English(EN)': 'If the sheets are in bad state but still usable, count 0.5 (1/2) a piece.'}",
                'isFlexField': True,
                'labelEn': 'Number of blankets/sheets',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of blankets/sheets',
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
                ],
                'hint': '{\'English(EN)\': "Put \'-1\', if there is no child. Take the youngest children of school going age. 0.5 for each upper piece of clothing and 0.5 for each lower piece of clothing"}',
                'isFlexField': True,
                'labelEn': "Number of complete children's clothes",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': "Number of complete children's clothes",
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
                'hint': '{\'English(EN)\': "Put \'-1\', if no women is present 1 complete set = 0.5 up ( eg Blouse/t-shirt)and 0.5 down (loincloths/skirts).The clothes of the mother or main woman in the household AND those of the oldest school aged girls in the house should be counted"}',
                'isFlexField': True,
                'labelEn': "Number of complete women's clothes",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': "Number of complete women's clothes",
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
                'hint': "{'English(EN)': 'Count the number of locally-made or imported ploughing tools.'}",
                'isFlexField': True,
                'labelEn': 'Number of ploughing tools',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Number of ploughing tools',
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
                        'value': '0'
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
                        'value': '1'
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
                    },
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
                'required': False,
                'type': 'SELECT_ONE'
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Other ID number',
                'labels': [
                    {
                        'label': 'Other ID number',
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
                    {
                        'labelEn': 'Repatriate',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': 'Population rapatriée – Personnes qui sont retournées chez elles, ou sont en cours de retours après avoir passée plusieurs semaines dans un pays étranger.',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Repatriate',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'repatriated'
                    },
                    {
                        'labelEn': 'Returnee',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': 'Population retournée – Personnes qui sont retournées dans leurs zone d’origine après avoir passée plusieurs semaines dans une autre region de la RCA',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Returnee',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'returnee'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Other Residence Status',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': 'Autres statut de résidence',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Other Residence Status',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'specific_residence_h_f',
                'required': False,
                'type': 'SELECT_ONE'
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
                'labelEn': 'Paid job with an organization/businesses (salaries, wages, bonuses, allowances, commissions, gratuities)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Paid job with an organization/businesses (salaries, wages, bonuses, allowances, commissions, gratuities)',
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Payment delivery phone number',
                'labels': [
                    {
                        'label': 'Payment delivery phone number',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'payment_delivery_phone_no',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Payment for self-employment (selling or making things, doing repairs, providing service, etc.)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Payment for self-employment (selling or making things, doing repairs, providing service, etc.)',
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Picture of the measured arm circumference',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': 'Prenez une photo de la mesure du périmètre brachial',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Picture of the measured arm circumference',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'arm_picture_i_f',
                'required': False,
                'type': 'IMAGE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Pregnant count',
                'labels': [
                    {
                        'label': 'Pregnant count',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'pregnant_count',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Profit from rental property you own',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Profit from rental property you own',
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
                        'value': '0'
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
                        'value': '1'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Pulses, nuts & seeds: beans, chickpeas, lentils',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Pulses, nuts & seeds: beans, chickpeas, lentils',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Purchased food on credit or borrowed food',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Purchased food on credit or borrowed food',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_buy_food_credit_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Reduce number of meals eaten in a day',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Reduce number of meals eaten in a day',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'red_coping_strategy_few_meals_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Reduced Coping Strategy Index (rCSI) Score',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Reduced Coping Strategy Index (rCSI) Score',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'RCSI_h_f',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
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
                'name': 'coping_strategy_red_exp_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Registration Data Import',
                'labels': [
                    {
                        'label': 'Registration Data Import',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'registration_data_import',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Registration Data Import',
                'labels': [
                    {
                        'label': 'Registration Data Import',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'registration_data_import',
                'required': False,
                'type': 'SELECT_MANY'
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
                        'labelEn': 'Foster child',
                        'labels': [
                            {
                                'label': 'Foster child',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FOSTER_CHILD'
                    },
                    {
                        'labelEn': 'Free union',
                        'labels': [
                            {
                                'label': 'Free union',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FREE_UNION'
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
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'OTHER'
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
                        'labelEn': 'Unknown',
                        'labels': [
                            {
                                'label': 'Unknown',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UNKNOWN'
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
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Rely on less preferred and less expensive foods',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Rely on less preferred and less expensive foods',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'red_coping_strategy_food_change_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Remittances from family (abroad or employed elsewhere)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Remittances from family (abroad or employed elsewhere)',
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
                    {
                        'labelEn': 'Displaced  |   Returnee',
                        'labels': [
                            {
                                'label': 'Displaced  |   Returnee',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RETURNEE'
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
                    },
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
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
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Restrict consumption by adults in order for small children to eat',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Restrict consumption by adults in order for small children to eat',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'red_coping_strategy_restrict_adult_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                    {
                        'labelEn': 'Alternate collector',
                        'labels': [
                            {
                                'label': 'Alternate collector',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ALTERNATE'
                    },
                    {
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NO_ROLE'
                    },
                    {
                        'labelEn': 'Primary collector',
                        'labels': [
                            {
                                'label': 'Primary collector',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRIMARY'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Role',
                'labels': [
                    {
                        'label': 'Role',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'role',
                'required': True,
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
                'type': 'INTEGER'
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
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Sale of assets (including livestock, land)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Sale of assets (including livestock, land)',
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
                'labelEn': 'Selling of your own agricultural production',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Selling of your own agricultural production',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
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
                'name': 'coping_strategy_adult_beg_h_f',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
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
                'name': 'coping_strategy_child_beg_h_f',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Sold house or land',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Sold house or land',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_sell_house_land_h_f',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Sold household assets/goods (jewelry, phone, furniture, electro domestics, etc)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Sold household assets/goods (jewelry, phone, furniture, electro domestics, etc)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_sell_assets_h_f',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Sold last female animals',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Sold last female animals',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_sell_fem_animals_h_f',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Sold productive assets or means of transport (sewing machine, wheelbarrow, bicycle, car, etc.)',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Sold productive assets or means of transport (sewing machine, wheelbarrow, bicycle, car, etc.)',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_sell_prod_assets_h_f',
                'required': False,
                'type': 'SELECT_ONE'
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Spent Savings',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Spent Savings',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_spent_savings_h_f',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Spent one or more days without eating',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': 'Passé un ou plusieurs jours sans manger',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Spent one or more days without eating',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_days_eating_h_f',
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
                        'value': '0'
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
                        'value': '1'
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
                        'value': '0'
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
                        'value': '1'
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
                'type': 'INTEGER'
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
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'UNHCR cash transfer',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'UNHCR cash transfer',
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
                'labelEn': 'UNICEF child cash grant',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'UNICEF child cash grant',
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
                        'value': '0'
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
                        'value': '1'
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
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'WFP assistance',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'WFP assistance',
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
                'type': 'INTEGER'
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
                        'labelEn': 'Ashes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Ashes',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'ashes'
                    },
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
                        'labelEn': 'None available',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'None available',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': 'none_available'
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
                'hint': "{'English(EN)': 'Select all that apply'}",
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
                'type': 'SELECT_MANY'
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
                'hint': '',
                'isFlexField': False,
                'labelEn': 'What is the Household size?',
                'labels': [
                    {
                        'label': 'What is the Household size?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'size',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the average daily income of the child?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the average daily income of the child?',
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': "What is the first name of ${full_name_i_c} 's grandmother?",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': "Quel est le prénom de la grand-mère de l'individu collecteur?",
                        'language': 'French(FR)'
                    },
                    {
                        'label': "What is the first name of ${full_name_i_c} 's grandmother?",
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'verif_primary_grandmother_i_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': "What is the first name of ${full_name_i_c} 's mother?",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': "Quel est le prénom de la mère de l'individu collecteur?",
                        'language': 'French(FR)'
                    },
                    {
                        'label': "What is the first name of ${full_name_i_c} 's mother?",
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'verif_primary_mother_i_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the first name of the eldest child of ${full_name_i_c} (girl or boy)?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': "Quel est le prénom de l'enfant ainé du collecteur (fille ou garçon)?",
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the first name of the eldest child of ${full_name_i_c} (girl or boy)?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'verif_primary_oldest_child_i_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the first name of the youngest child of ${full_name_i_c} (girl or boy)?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': "Quel est le prénom de l'enfant cadet du collecteur (fille ou garçon)?",
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the first name of the youngest child of ${full_name_i_c} (girl or boy)?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'verif_primary_youngest_child_i_f',
                'required': False,
                'type': 'STRING'
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
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': "What is the main reason for your household's choice to assume debt?",
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': "What is the main reason for your household's choice to assume debt?",
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'debt_reason_h_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'What is the number of children in the Household?',
                'labels': [
                    {
                        'label': 'What is the number of children in the Household?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'number_of_children',
                'required': False,
                'type': 'INTEGER'
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
                    {
                        'labelEn': 'Packaged water (bottled water, sachets, …)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Packaged water (bottled water, sachets, …)',
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the village of origin of ${full_name_i_c}?',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': 'Quel est le village d’origine\xa0du collecteur?',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the village of origin of ${full_name_i_c}?',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'verif_primary_origin_i_f',
                'required': False,
                'type': 'STRING'
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
                        'labelEn': 'Packaged water (bottled water, sachets, …)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Packaged water (bottled water, sachets, …)',
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
                        'labelEn': 'Afghan afghani',
                        'labels': [
                            {
                                'label': 'Afghan afghani',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AFN'
                    },
                    {
                        'labelEn': 'Albanian lek',
                        'labels': [
                            {
                                'label': 'Albanian lek',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ALL'
                    },
                    {
                        'labelEn': 'Algerian dinar',
                        'labels': [
                            {
                                'label': 'Algerian dinar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DZD'
                    },
                    {
                        'labelEn': 'Angolan kwanza',
                        'labels': [
                            {
                                'label': 'Angolan kwanza',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AOA'
                    },
                    {
                        'labelEn': 'Argentine peso',
                        'labels': [
                            {
                                'label': 'Argentine peso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ARS'
                    },
                    {
                        'labelEn': 'Armenian dram',
                        'labels': [
                            {
                                'label': 'Armenian dram',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AMD'
                    },
                    {
                        'labelEn': 'Aruban florin',
                        'labels': [
                            {
                                'label': 'Aruban florin',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AWG'
                    },
                    {
                        'labelEn': 'Australian dollar',
                        'labels': [
                            {
                                'label': 'Australian dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AUD'
                    },
                    {
                        'labelEn': 'Azerbaijani manat',
                        'labels': [
                            {
                                'label': 'Azerbaijani manat',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AZN'
                    },
                    {
                        'labelEn': 'Bahamian dollar',
                        'labels': [
                            {
                                'label': 'Bahamian dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BSD'
                    },
                    {
                        'labelEn': 'Bahraini dinar',
                        'labels': [
                            {
                                'label': 'Bahraini dinar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BHD'
                    },
                    {
                        'labelEn': 'Bangladeshi taka',
                        'labels': [
                            {
                                'label': 'Bangladeshi taka',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BDT'
                    },
                    {
                        'labelEn': 'Barbados dollar',
                        'labels': [
                            {
                                'label': 'Barbados dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BBD'
                    },
                    {
                        'labelEn': 'Belarusian ruble',
                        'labels': [
                            {
                                'label': 'Belarusian ruble',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BYN'
                    },
                    {
                        'labelEn': 'Belize dollar',
                        'labels': [
                            {
                                'label': 'Belize dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BZD'
                    },
                    {
                        'labelEn': 'Bermudian dollar',
                        'labels': [
                            {
                                'label': 'Bermudian dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BMD'
                    },
                    {
                        'labelEn': 'Bhutanese ngultrum',
                        'labels': [
                            {
                                'label': 'Bhutanese ngultrum',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BTN'
                    },
                    {
                        'labelEn': 'Bolivian Mvdol (funds code)',
                        'labels': [
                            {
                                'label': 'Bolivian Mvdol (funds code)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BOV'
                    },
                    {
                        'labelEn': 'Boliviano',
                        'labels': [
                            {
                                'label': 'Boliviano',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BOB'
                    },
                    {
                        'labelEn': 'Bosnia and Herzegovina convertible mark',
                        'labels': [
                            {
                                'label': 'Bosnia and Herzegovina convertible mark',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BAM'
                    },
                    {
                        'labelEn': 'Botswana pula',
                        'labels': [
                            {
                                'label': 'Botswana pula',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BWP'
                    },
                    {
                        'labelEn': 'Brazilian real',
                        'labels': [
                            {
                                'label': 'Brazilian real',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BRL'
                    },
                    {
                        'labelEn': 'Brunei dollar',
                        'labels': [
                            {
                                'label': 'Brunei dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BND'
                    },
                    {
                        'labelEn': 'Bulgarian lev',
                        'labels': [
                            {
                                'label': 'Bulgarian lev',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BGN'
                    },
                    {
                        'labelEn': 'Burundian franc',
                        'labels': [
                            {
                                'label': 'Burundian franc',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BIF'
                    },
                    {
                        'labelEn': 'CFA franc BCEAO',
                        'labels': [
                            {
                                'label': 'CFA franc BCEAO',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'XOF'
                    },
                    {
                        'labelEn': 'CFA franc BEAC',
                        'labels': [
                            {
                                'label': 'CFA franc BEAC',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'XAF'
                    },
                    {
                        'labelEn': 'CFP franc (franc Pacifique)',
                        'labels': [
                            {
                                'label': 'CFP franc (franc Pacifique)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'XPF'
                    },
                    {
                        'labelEn': 'Cambodian riel',
                        'labels': [
                            {
                                'label': 'Cambodian riel',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KHR'
                    },
                    {
                        'labelEn': 'Canadian dollar',
                        'labels': [
                            {
                                'label': 'Canadian dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CAD'
                    },
                    {
                        'labelEn': 'Cape Verdean escudo',
                        'labels': [
                            {
                                'label': 'Cape Verdean escudo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CVE'
                    },
                    {
                        'labelEn': 'Cayman Islands dollar',
                        'labels': [
                            {
                                'label': 'Cayman Islands dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KYD'
                    },
                    {
                        'labelEn': 'Chilean peso',
                        'labels': [
                            {
                                'label': 'Chilean peso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CLP'
                    },
                    {
                        'labelEn': 'Chinese yuan',
                        'labels': [
                            {
                                'label': 'Chinese yuan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CNY'
                    },
                    {
                        'labelEn': 'Colombian peso',
                        'labels': [
                            {
                                'label': 'Colombian peso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COP'
                    },
                    {
                        'labelEn': 'Comoro franc',
                        'labels': [
                            {
                                'label': 'Comoro franc',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KMF'
                    },
                    {
                        'labelEn': 'Congolese franc',
                        'labels': [
                            {
                                'label': 'Congolese franc',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CDF'
                    },
                    {
                        'labelEn': 'Costa Rican colon',
                        'labels': [
                            {
                                'label': 'Costa Rican colon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CRC'
                    },
                    {
                        'labelEn': 'Croatian kuna',
                        'labels': [
                            {
                                'label': 'Croatian kuna',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HRK'
                    },
                    {
                        'labelEn': 'Cuban convertible peso',
                        'labels': [
                            {
                                'label': 'Cuban convertible peso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CUC'
                    },
                    {
                        'labelEn': 'Cuban peso',
                        'labels': [
                            {
                                'label': 'Cuban peso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CUP'
                    },
                    {
                        'labelEn': 'Czech koruna',
                        'labels': [
                            {
                                'label': 'Czech koruna',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CZK'
                    },
                    {
                        'labelEn': 'Danish krone',
                        'labels': [
                            {
                                'label': 'Danish krone',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DKK'
                    },
                    {
                        'labelEn': 'Djiboutian franc',
                        'labels': [
                            {
                                'label': 'Djiboutian franc',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DJF'
                    },
                    {
                        'labelEn': 'Dominican peso',
                        'labels': [
                            {
                                'label': 'Dominican peso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DOP'
                    },
                    {
                        'labelEn': 'East Caribbean dollar',
                        'labels': [
                            {
                                'label': 'East Caribbean dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'XCD'
                    },
                    {
                        'labelEn': 'Egyptian pound',
                        'labels': [
                            {
                                'label': 'Egyptian pound',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EGP'
                    },
                    {
                        'labelEn': 'Eritrean nakfa',
                        'labels': [
                            {
                                'label': 'Eritrean nakfa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ERN'
                    },
                    {
                        'labelEn': 'Ethiopian birr',
                        'labels': [
                            {
                                'label': 'Ethiopian birr',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ETB'
                    },
                    {
                        'labelEn': 'Euro',
                        'labels': [
                            {
                                'label': 'Euro',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EUR'
                    },
                    {
                        'labelEn': 'Falkland Islands pound',
                        'labels': [
                            {
                                'label': 'Falkland Islands pound',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FKP'
                    },
                    {
                        'labelEn': 'Fiji dollar',
                        'labels': [
                            {
                                'label': 'Fiji dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FJD'
                    },
                    {
                        'labelEn': 'Gambian dalasi',
                        'labels': [
                            {
                                'label': 'Gambian dalasi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GMD'
                    },
                    {
                        'labelEn': 'Georgian lari',
                        'labels': [
                            {
                                'label': 'Georgian lari',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GEL'
                    },
                    {
                        'labelEn': 'Ghanaian cedi',
                        'labels': [
                            {
                                'label': 'Ghanaian cedi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GHS'
                    },
                    {
                        'labelEn': 'Gibraltar pound',
                        'labels': [
                            {
                                'label': 'Gibraltar pound',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GIP'
                    },
                    {
                        'labelEn': 'Gold (one troy ounce)',
                        'labels': [
                            {
                                'label': 'Gold (one troy ounce)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'XAU'
                    },
                    {
                        'labelEn': 'Guatemalan quetzal',
                        'labels': [
                            {
                                'label': 'Guatemalan quetzal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GTQ'
                    },
                    {
                        'labelEn': 'Guinean franc',
                        'labels': [
                            {
                                'label': 'Guinean franc',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GNF'
                    },
                    {
                        'labelEn': 'Guyanese dollar',
                        'labels': [
                            {
                                'label': 'Guyanese dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GYD'
                    },
                    {
                        'labelEn': 'Haitian gourde',
                        'labels': [
                            {
                                'label': 'Haitian gourde',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HTG'
                    },
                    {
                        'labelEn': 'Honduran lempira',
                        'labels': [
                            {
                                'label': 'Honduran lempira',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HNL'
                    },
                    {
                        'labelEn': 'Hong Kong dollar',
                        'labels': [
                            {
                                'label': 'Hong Kong dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HKD'
                    },
                    {
                        'labelEn': 'Hungarian forint',
                        'labels': [
                            {
                                'label': 'Hungarian forint',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HUF'
                    },
                    {
                        'labelEn': 'Icelandic króna',
                        'labels': [
                            {
                                'label': 'Icelandic króna',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ISK'
                    },
                    {
                        'labelEn': 'Indian rupee',
                        'labels': [
                            {
                                'label': 'Indian rupee',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'INR'
                    },
                    {
                        'labelEn': 'Indonesian rupiah',
                        'labels': [
                            {
                                'label': 'Indonesian rupiah',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IDR'
                    },
                    {
                        'labelEn': 'Iranian rial',
                        'labels': [
                            {
                                'label': 'Iranian rial',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IRR'
                    },
                    {
                        'labelEn': 'Iraqi dinar',
                        'labels': [
                            {
                                'label': 'Iraqi dinar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IQD'
                    },
                    {
                        'labelEn': 'Israeli new shekel',
                        'labels': [
                            {
                                'label': 'Israeli new shekel',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ILS'
                    },
                    {
                        'labelEn': 'Jamaican dollar',
                        'labels': [
                            {
                                'label': 'Jamaican dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JMD'
                    },
                    {
                        'labelEn': 'Japanese yen',
                        'labels': [
                            {
                                'label': 'Japanese yen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JPY'
                    },
                    {
                        'labelEn': 'Jordanian dinar',
                        'labels': [
                            {
                                'label': 'Jordanian dinar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JOD'
                    },
                    {
                        'labelEn': 'Kazakhstani tenge',
                        'labels': [
                            {
                                'label': 'Kazakhstani tenge',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KZT'
                    },
                    {
                        'labelEn': 'Kenyan shilling',
                        'labels': [
                            {
                                'label': 'Kenyan shilling',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KES'
                    },
                    {
                        'labelEn': 'Kuwaiti dinar',
                        'labels': [
                            {
                                'label': 'Kuwaiti dinar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KWD'
                    },
                    {
                        'labelEn': 'Kyrgyzstani som',
                        'labels': [
                            {
                                'label': 'Kyrgyzstani som',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KGS'
                    },
                    {
                        'labelEn': 'Lao kip',
                        'labels': [
                            {
                                'label': 'Lao kip',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LAK'
                    },
                    {
                        'labelEn': 'Lebanese pound',
                        'labels': [
                            {
                                'label': 'Lebanese pound',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LBP'
                    },
                    {
                        'labelEn': 'Lesotho loti',
                        'labels': [
                            {
                                'label': 'Lesotho loti',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LSL'
                    },
                    {
                        'labelEn': 'Liberian dollar',
                        'labels': [
                            {
                                'label': 'Liberian dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LRD'
                    },
                    {
                        'labelEn': 'Libyan dinar',
                        'labels': [
                            {
                                'label': 'Libyan dinar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LYD'
                    },
                    {
                        'labelEn': 'Macanese pataca',
                        'labels': [
                            {
                                'label': 'Macanese pataca',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MOP'
                    },
                    {
                        'labelEn': 'Macedonian denar',
                        'labels': [
                            {
                                'label': 'Macedonian denar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MKD'
                    },
                    {
                        'labelEn': 'Malagasy ariary',
                        'labels': [
                            {
                                'label': 'Malagasy ariary',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MGA'
                    },
                    {
                        'labelEn': 'Malawian kwacha',
                        'labels': [
                            {
                                'label': 'Malawian kwacha',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MWK'
                    },
                    {
                        'labelEn': 'Malaysian ringgit',
                        'labels': [
                            {
                                'label': 'Malaysian ringgit',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MYR'
                    },
                    {
                        'labelEn': 'Maldivian rufiyaa',
                        'labels': [
                            {
                                'label': 'Maldivian rufiyaa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MVR'
                    },
                    {
                        'labelEn': 'Mauritanian ouguiya',
                        'labels': [
                            {
                                'label': 'Mauritanian ouguiya',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MRU'
                    },
                    {
                        'labelEn': 'Mauritian rupee',
                        'labels': [
                            {
                                'label': 'Mauritian rupee',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MUR'
                    },
                    {
                        'labelEn': 'Mexican peso',
                        'labels': [
                            {
                                'label': 'Mexican peso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MXN'
                    },
                    {
                        'labelEn': 'Moldovan leu',
                        'labels': [
                            {
                                'label': 'Moldovan leu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MDL'
                    },
                    {
                        'labelEn': 'Mongolian tögrög',
                        'labels': [
                            {
                                'label': 'Mongolian tögrög',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MNT'
                    },
                    {
                        'labelEn': 'Moroccan dirham',
                        'labels': [
                            {
                                'label': 'Moroccan dirham',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MAD'
                    },
                    {
                        'labelEn': 'Mozambican metical',
                        'labels': [
                            {
                                'label': 'Mozambican metical',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MZN'
                    },
                    {
                        'labelEn': 'Myanmar kyat',
                        'labels': [
                            {
                                'label': 'Myanmar kyat',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MMK'
                    },
                    {
                        'labelEn': 'Namibian dollar',
                        'labels': [
                            {
                                'label': 'Namibian dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NAD'
                    },
                    {
                        'labelEn': 'Nepalese rupee',
                        'labels': [
                            {
                                'label': 'Nepalese rupee',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NPR'
                    },
                    {
                        'labelEn': 'Netherlands Antillean guilder',
                        'labels': [
                            {
                                'label': 'Netherlands Antillean guilder',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ANG'
                    },
                    {
                        'labelEn': 'New Taiwan dollar',
                        'labels': [
                            {
                                'label': 'New Taiwan dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TWD'
                    },
                    {
                        'labelEn': 'New Zealand dollar',
                        'labels': [
                            {
                                'label': 'New Zealand dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NZD'
                    },
                    {
                        'labelEn': 'Nicaraguan córdoba',
                        'labels': [
                            {
                                'label': 'Nicaraguan córdoba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NIO'
                    },
                    {
                        'labelEn': 'Nigerian naira',
                        'labels': [
                            {
                                'label': 'Nigerian naira',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NGN'
                    },
                    {
                        'labelEn': 'North Korean won',
                        'labels': [
                            {
                                'label': 'North Korean won',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KPW'
                    },
                    {
                        'labelEn': 'Norwegian krone',
                        'labels': [
                            {
                                'label': 'Norwegian krone',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NOK'
                    },
                    {
                        'labelEn': 'Omani rial',
                        'labels': [
                            {
                                'label': 'Omani rial',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'OMR'
                    },
                    {
                        'labelEn': 'Pakistani rupee',
                        'labels': [
                            {
                                'label': 'Pakistani rupee',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PKR'
                    },
                    {
                        'labelEn': 'Panamanian balboa',
                        'labels': [
                            {
                                'label': 'Panamanian balboa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PAB'
                    },
                    {
                        'labelEn': 'Papua New Guinean kina',
                        'labels': [
                            {
                                'label': 'Papua New Guinean kina',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PGK'
                    },
                    {
                        'labelEn': 'Paraguayan guaraní',
                        'labels': [
                            {
                                'label': 'Paraguayan guaraní',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PYG'
                    },
                    {
                        'labelEn': 'Peruvian sol',
                        'labels': [
                            {
                                'label': 'Peruvian sol',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PEN'
                    },
                    {
                        'labelEn': 'Philippine peso',
                        'labels': [
                            {
                                'label': 'Philippine peso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PHP'
                    },
                    {
                        'labelEn': 'Polish złoty',
                        'labels': [
                            {
                                'label': 'Polish złoty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PLN'
                    },
                    {
                        'labelEn': 'Pound sterling',
                        'labels': [
                            {
                                'label': 'Pound sterling',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GBP'
                    },
                    {
                        'labelEn': 'Qatari riyal',
                        'labels': [
                            {
                                'label': 'Qatari riyal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'QAR'
                    },
                    {
                        'labelEn': 'Romanian leu',
                        'labels': [
                            {
                                'label': 'Romanian leu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RON'
                    },
                    {
                        'labelEn': 'Russian ruble',
                        'labels': [
                            {
                                'label': 'Russian ruble',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RUB'
                    },
                    {
                        'labelEn': 'Rwandan franc',
                        'labels': [
                            {
                                'label': 'Rwandan franc',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RWF'
                    },
                    {
                        'labelEn': 'Saint Helena pound',
                        'labels': [
                            {
                                'label': 'Saint Helena pound',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SHP'
                    },
                    {
                        'labelEn': 'Salvadoran colón',
                        'labels': [
                            {
                                'label': 'Salvadoran colón',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SVC'
                    },
                    {
                        'labelEn': 'Samoan tala',
                        'labels': [
                            {
                                'label': 'Samoan tala',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WST'
                    },
                    {
                        'labelEn': 'Saudi riyal',
                        'labels': [
                            {
                                'label': 'Saudi riyal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SAR'
                    },
                    {
                        'labelEn': 'Serbian dinar',
                        'labels': [
                            {
                                'label': 'Serbian dinar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RSD'
                    },
                    {
                        'labelEn': 'Seychelles rupee',
                        'labels': [
                            {
                                'label': 'Seychelles rupee',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SCR'
                    },
                    {
                        'labelEn': 'Sierra Leonean leone',
                        'labels': [
                            {
                                'label': 'Sierra Leonean leone',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SLE'
                    },
                    {
                        'labelEn': 'Silver (one troy ounce)',
                        'labels': [
                            {
                                'label': 'Silver (one troy ounce)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'XAG'
                    },
                    {
                        'labelEn': 'Singapore dollar',
                        'labels': [
                            {
                                'label': 'Singapore dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SGD'
                    },
                    {
                        'labelEn': 'Solomon Islands dollar',
                        'labels': [
                            {
                                'label': 'Solomon Islands dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SBD'
                    },
                    {
                        'labelEn': 'Somali shilling',
                        'labels': [
                            {
                                'label': 'Somali shilling',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SOS'
                    },
                    {
                        'labelEn': 'South African rand',
                        'labels': [
                            {
                                'label': 'South African rand',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZAR'
                    },
                    {
                        'labelEn': 'South Korean won',
                        'labels': [
                            {
                                'label': 'South Korean won',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KRW'
                    },
                    {
                        'labelEn': 'South Sudanese pound',
                        'labels': [
                            {
                                'label': 'South Sudanese pound',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SSP'
                    },
                    {
                        'labelEn': 'Sri Lankan rupee',
                        'labels': [
                            {
                                'label': 'Sri Lankan rupee',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LKR'
                    },
                    {
                        'labelEn': 'Sudanese pound',
                        'labels': [
                            {
                                'label': 'Sudanese pound',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SDG'
                    },
                    {
                        'labelEn': 'Surinamese dollar',
                        'labels': [
                            {
                                'label': 'Surinamese dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SRD'
                    },
                    {
                        'labelEn': 'Swazi lilangeni',
                        'labels': [
                            {
                                'label': 'Swazi lilangeni',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SZL'
                    },
                    {
                        'labelEn': 'Swedish krona/kronor',
                        'labels': [
                            {
                                'label': 'Swedish krona/kronor',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SEK'
                    },
                    {
                        'labelEn': 'Swiss franc',
                        'labels': [
                            {
                                'label': 'Swiss franc',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CHF'
                    },
                    {
                        'labelEn': 'Syrian pound',
                        'labels': [
                            {
                                'label': 'Syrian pound',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SYP'
                    },
                    {
                        'labelEn': 'São Tomé and Príncipe dobra',
                        'labels': [
                            {
                                'label': 'São Tomé and Príncipe dobra',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'STN'
                    },
                    {
                        'labelEn': 'Tajikistani somoni',
                        'labels': [
                            {
                                'label': 'Tajikistani somoni',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TJS'
                    },
                    {
                        'labelEn': 'Tanzanian shilling',
                        'labels': [
                            {
                                'label': 'Tanzanian shilling',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TZS'
                    },
                    {
                        'labelEn': 'Thai baht',
                        'labels': [
                            {
                                'label': 'Thai baht',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'THB'
                    },
                    {
                        'labelEn': 'Tongan paʻanga',
                        'labels': [
                            {
                                'label': 'Tongan paʻanga',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TOP'
                    },
                    {
                        'labelEn': 'Trinidad and Tobago dollar',
                        'labels': [
                            {
                                'label': 'Trinidad and Tobago dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TTD'
                    },
                    {
                        'labelEn': 'Tunisian dinar',
                        'labels': [
                            {
                                'label': 'Tunisian dinar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TND'
                    },
                    {
                        'labelEn': 'Turkish lira',
                        'labels': [
                            {
                                'label': 'Turkish lira',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TRY'
                    },
                    {
                        'labelEn': 'Turkmenistan manat',
                        'labels': [
                            {
                                'label': 'Turkmenistan manat',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TMT'
                    },
                    {
                        'labelEn': 'USD Coin',
                        'labels': [
                            {
                                'label': 'USD Coin',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'USDC'
                    },
                    {
                        'labelEn': 'Ugandan shilling',
                        'labels': [
                            {
                                'label': 'Ugandan shilling',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UGX'
                    },
                    {
                        'labelEn': 'Ukrainian hryvnia',
                        'labels': [
                            {
                                'label': 'Ukrainian hryvnia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UAH'
                    },
                    {
                        'labelEn': 'Unidad previsional[14]',
                        'labels': [
                            {
                                'label': 'Unidad previsional[14]',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UYW'
                    },
                    {
                        'labelEn': 'United Arab Emirates dirham',
                        'labels': [
                            {
                                'label': 'United Arab Emirates dirham',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AED'
                    },
                    {
                        'labelEn': 'United States dollar',
                        'labels': [
                            {
                                'label': 'United States dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'USD'
                    },
                    {
                        'labelEn': 'Uruguayan peso',
                        'labels': [
                            {
                                'label': 'Uruguayan peso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UYU'
                    },
                    {
                        'labelEn': 'Uzbekistan som',
                        'labels': [
                            {
                                'label': 'Uzbekistan som',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UZS'
                    },
                    {
                        'labelEn': 'Vanuatu vatu',
                        'labels': [
                            {
                                'label': 'Vanuatu vatu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VUV'
                    },
                    {
                        'labelEn': 'Venezuelan bolívar soberano',
                        'labels': [
                            {
                                'label': 'Venezuelan bolívar soberano',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VES'
                    },
                    {
                        'labelEn': 'Vietnamese đồng',
                        'labels': [
                            {
                                'label': 'Vietnamese đồng',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VND'
                    },
                    {
                        'labelEn': 'Yemeni rial',
                        'labels': [
                            {
                                'label': 'Yemeni rial',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'YER'
                    },
                    {
                        'labelEn': 'Zambian kwacha',
                        'labels': [
                            {
                                'label': 'Zambian kwacha',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZMW'
                    },
                    {
                        'labelEn': 'Zimbabwean dollar',
                        'labels': [
                            {
                                'label': 'Zimbabwean dollar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZWL'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Which currency will be used for financial questions?',
                'labels': [
                    {
                        'label': 'Which currency will be used for financial questions?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'currency',
                'required': False,
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
                        'labelEn': 'None',
                        'labels': [
                            {
                                'label': 'None',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': ''
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
                'required': False,
                'type': 'SELECT_MANY'
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
                        'value': '0'
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
                        'value': '1'
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
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Who answers this (alt) phone?',
                'labels': [
                    {
                        'label': 'Who answers this (alt) phone?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'who_answers_alt_phone',
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
                'name': 'who_answers_phone',
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
                        'value': '1'
                    },
                    {
                        'labelEn': 'No, because I have already engaged in this activity and cannot continue to do it.',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, because I have already engaged in this activity and cannot continue to do it.',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '2'
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
                        'value': '3'
                    },
                    {
                        'labelEn': 'Not Applicable',
                        'labels': [
                            {
                                'label': '',
                                'language': 'Arabic(AR)'
                            },
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Applicable',
                                'language': 'English(EN)'
                            },
                            {
                                'label': '',
                                'language': 'Spanish(ES)'
                            }
                        ],
                        'value': '4'
                    }
                ],
                'hint': "{'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Withdrew children from school',
                'labels': [
                    {
                        'label': '',
                        'language': 'Arabic(AR)'
                    },
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Withdrew children from school',
                        'language': 'English(EN)'
                    },
                    {
                        'label': '',
                        'language': 'Spanish(ES)'
                    }
                ],
                'name': 'coping_strategy_school_h_f',
                'required': False,
                'type': 'SELECT_ONE'
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
            }
        ]
    }
}
