# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestMetaDataFilterType::test_core_meta_type_query 1'] = {
    'data': {
        'allFieldsAttributes': [
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '0'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Does your family host an unaccompanied child / fosterchild?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Does your family host an unaccompanied child / fosterchild?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'unaccompanied_child_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '0'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Has any of your children been ill with cough and fever at any time in the last 2 weeks?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Has any of your children been ill with cough and fever at any time in the last 2 weeks?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'recent_illness_child_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '0'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If any child was sick, When he/she had an illness with a cough, did he/she breathe faster than usual with short, rapid breaths or have difficulty breathing?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If any child was sick, When he/she had an illness with a cough, did he/she breathe faster than usual with short, rapid breaths or have difficulty breathing?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'difficulty_breathing_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '0'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If above is Yes, did you seek advice or treatment for the illness from any source?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If above is Yes, did you seek advice or treatment for the illness from any source?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'treatment_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'Government Hospital',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Government Hospital',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'governent_health_center'
                    },
                    {
                        'labelEn': 'Government Health Center',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Government Health Center',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'governent_hospital'
                    },
                    {
                        'labelEn': 'Other Public',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other Public',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'other_public'
                    },
                    {
                        'labelEn': 'Private Hospital/Clinic',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Private Hospital/Clinic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'private_hospital'
                    },
                    {
                        'labelEn': 'Pharmacy',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Pharmacy',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'pharmacy'
                    },
                    {
                        'labelEn': 'Private Doctor',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Private Doctor',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'private_doctor'
                    },
                    {
                        'labelEn': 'Other Private',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other Private',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'other_private'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Where did you seek advice or treatment?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Where did you seek advice or treatment?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'treatment_facility_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If other, specify',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If other, specify',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'other_treatment_facility_h_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'Own the place I live in',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Own the place I live in',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'own'
                    },
                    {
                        'labelEn': 'Rent the place I live in with a formal contract',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rent the place I live in with a formal contract',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'rent_formal_contract'
                    },
                    {
                        'labelEn': 'Rent the place I live in with an informal contract',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Rent the place I live in with an informal contract',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'rent_informal_contract'
                    },
                    {
                        'labelEn': 'Accommodation is free / other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Accommodation is free / other',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'free_accomodation'
                    },
                    {
                        'labelEn': 'Informal settlement',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Informal settlement',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'informal settlement'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is your living situation?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is your living situation?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'living_situation_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the number of rooms in your dwelling excluding kitchen & bathroom?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the number of rooms in your dwelling excluding kitchen & bathroom?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'number_of_rooms_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the total number of people living in your dwelling?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the total number of people living in your dwelling?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'total_dwellers_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If there is more than one bedroom, what is the highest number of individuals living in one room?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If there is more than one bedroom, what is the highest number of individuals living in one room?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'one_room_dwellers_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Total number of households in the same living space?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Total number of households in the same living space?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'total_households_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'Buy bottled water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Buy bottled water',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'bottle_water'
                    },
                    {
                        'labelEn': 'From piped water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'From piped water',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'piped_water'
                    },
                    {
                        'labelEn': 'From private vendor',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'From private vendor',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'private_vendor_water'
                    },
                    {
                        'labelEn': 'To buy water from water tank',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'To buy water from water tank',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'water_tank'
                    },
                    {
                        'labelEn': 'Collect water from rain water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Collect water from rain water',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'rain_water'
                    },
                    {
                        'labelEn': 'Collect water from a well/source directly',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Collect water from a well/source directly',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'well_water'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is your primary source of drinking water?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is your primary source of drinking water?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'water_source_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'Yes, it is sufficient for our needs',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes, it is sufficient for our needs',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'sufficientwater'
                    },
                    {
                        'labelEn': 'Yes, somehow It is not always enough, especially in Summer',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes, somehow It is not always enough, especially in Summer',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'partiallysufficientwater'
                    },
                    {
                        'labelEn': 'No, everyday our family struggles because of lack of water',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, everyday our family struggles because of lack of water',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'insufficientwater'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Is water sufficient for all your uses in the household?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Is water sufficient for all your uses in the household?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'sufficient_water_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'No, only my household has access',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No, only my household has access',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'not_shared'
                    },
                    {
                        'labelEn': 'Yes, with one other household',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes, with one other household',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'shared_with_two_hh'
                    },
                    {
                        'labelEn': 'Yes, with two or more households',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes, with two or more households',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'shared_with_one_hh'
                    },
                    {
                        'labelEn': 'No facility (open defection)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No facility (open defection)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'no_latrine'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Do you share a latrine?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Do you share a latrine?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'latrine_h_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Yesterday, how many meals were eaten by your family?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Yesterday, how many meals were eaten by your family?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'meals_yesterday_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'In the last 7 days, how many days did you consume the following?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'In the last 7 days, how many days did you consume the following?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'food_consumption_h_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Cereals, grains, roots & tubers: rice, pasta, bread, bulgur',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Cereals, grains, roots & tubers: rice, pasta, bread, bulgur',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'cereals_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'White tubers & roots (potato, sweet potato)',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'White tubers & roots (potato, sweet potato)',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'tubers_roots_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Vegetables & leaves: spinach, cucumber, eggplant, tomato',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Vegetables & leaves: spinach, cucumber, eggplant, tomato',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'vegetables_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Fruits: citrus, apple, banana, dates',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Fruits: citrus, apple, banana, dates',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'fruits_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Meat, fish and eggs: Beef, lamb chicken, liver, kidney, fish including canned tuna, eggs',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Meat, fish and eggs: Beef, lamb chicken, liver, kidney, fish including canned tuna, eggs',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'meat_fish_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Pulses, nuts & seeds : beans, chickpeas, lentils',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Pulses, nuts & seeds : beans, chickpeas, lentils',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'pulses_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Milk and dairy products: yoghurt, cheese',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Milk and dairy products: yoghurt, cheese',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'dairy_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Oil / fat: vegetable oil, palm oil, butter, ghee',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Oil / fat: vegetable oil, palm oil, butter, ghee',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'oilfat_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Sugar / sweets: honey, cakes, sugary drinks, (this includes sugar used in tea)',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Sugar / sweets: honey, cakes, sugary drinks, (this includes sugar used in tea)',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'sugarsweet_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Condiments / spices: tea, garlic, tomato sauce including small amount of milk used in tea coffee',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Condiments / spices: tea, garlic, tomato sauce including small amount of milk used in tea coffee',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'condiments_h_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'No assistrance received',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No assistrance received',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'no_assistance'
                    },
                    {
                        'labelEn': 'Food assistance in-kind support',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Food assistance in-kind support',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'food_in_kind'
                    },
                    {
                        'labelEn': 'Food assistance vouchers',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Food assistance vouchers',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'food_vouchers'
                    },
                    {
                        'labelEn': 'Food assistance for children',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Food assistance for children',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'food_for_children'
                    },
                    {
                        'labelEn': 'Cash assistance',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Cash assistance',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'cash_assistance'
                    },
                    {
                        'labelEn': 'Child cash grant',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child cash grant',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'child_cash_grant'
                    },
                    {
                        'labelEn': 'Voucher',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Voucher',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'voucher'
                    },
                    {
                        'labelEn': 'School feeding',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'School feeding',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'school_feeding'
                    },
                    {
                        'labelEn': 'School material',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'School material',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'school_material'
                    },
                    {
                        'labelEn': 'Child education grant',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Child education grant',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'child_edu_grant'
                    },
                    {
                        'labelEn': 'Informal education',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Informal education',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'informal_education'
                    },
                    {
                        'labelEn': 'Health medical services',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Health medical services',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'health_services'
                    },
                    {
                        'labelEn': 'Training',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Training',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'training'
                    },
                    {
                        'labelEn': 'Psychosocial services',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Psychosocial services',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'psychosocial'
                    },
                    {
                        'labelEn': 'Job opportunities',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Job opportunities',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'job_opportunities'
                    },
                    {
                        'labelEn': 'Winterization assistance',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Winterization assistance',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'winterization'
                    },
                    {
                        'labelEn': 'None of the above',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'None of the above',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'none'
                    },
                    {
                        'labelEn': "Don't Know",
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': "Don't Know",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'don’t_know'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What type of assistance did your family receive in the past six months?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What type of assistance did your family receive in the past six months?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'assistance_type_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': '0',
                'choices': [
                    {
                        'labelEn': 'UNICEF',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'UNICEF',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'unicef'
                    },
                    {
                        'labelEn': 'UNHCR',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'UNHCR',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'unhcr'
                    },
                    {
                        'labelEn': 'WFP',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'WFP',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'wfp'
                    },
                    {
                        'labelEn': 'NGOs, religious organizations and CBOs',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'NGOs, religious organizations and CBOs',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ngos'
                    },
                    {
                        'labelEn': 'Other INGO (non UN related)',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other INGO (non UN related)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'other_ingo'
                    },
                    {
                        'labelEn': 'Relatives/friends/neighbors',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Relatives/friends/neighbors',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'relatives_friends'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'other'
                    },
                    {
                        'labelEn': "Don't know",
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': "Don't know",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'don’t_know'
                    },
                    {
                        'labelEn': 'Governmental',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Governmental',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'governmental'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Did your family get assistance from any of these sources in the last 6 months?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Did your family get assistance from any of these sources in the last 6 months?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'assistance_source_h_f',
                'required': False,
                'type': 'SELECT_MANY'
            },
            {
                'associatedWith': '1',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Photo',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Photo',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'photo_i_f',
                'required': False,
                'type': 'IMAGE'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Birth Certificate',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Birth Certificate',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'birth_certificate'
                    },
                    {
                        'labelEn': "Driver's License",
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': "Driver's License",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'drivers_licence'
                    },
                    {
                        'labelEn': 'UNHCR ID',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'UNHCR ID',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'unhcr_id'
                    },
                    {
                        'labelEn': 'National ID',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'National ID',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'national_id'
                    },
                    {
                        'labelEn': 'National Passport',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'National Passport',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'national_passp'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'other'
                    },
                    {
                        'labelEn': 'Not Available',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Not Available',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'not_available'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What type of identification document is provided?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What type of identification document is provided?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'id_type_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If other, specify',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If other, specify',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'other_id_type_i_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': '1',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What is the ID number on the document?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What is the ID number on the document?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'id_no_i_f',
                'required': False,
                'type': 'STRING'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'some_difficulty'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'lot_difficulty'
                    },
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'cannot_do'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If member has difficulty seeing, what is the severity?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If member has difficulty seeing, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'seeing_disability_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'some_difficulty'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'lot_difficulty'
                    },
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'cannot_do'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If member has difficulty hearing, what is the severity?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If member has difficulty hearing, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'hearing_disability_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'some_difficulty'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'lot_difficulty'
                    },
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'cannot_do'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If member has difficulty walking or climbing steps, what is the severity?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If member has difficulty walking or climbing steps, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'physical_disability_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'some_difficulty'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'lot_difficulty'
                    },
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'cannot_do'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If member has difficulty remembering or concentrating, what is the severity?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If member has difficulty remembering or concentrating, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'memory_disability_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'some_difficulty'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'lot_difficulty'
                    },
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'cannot_do'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'Do you have difficulty (with self-care such as) washing all over or dressing',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'Do you have difficulty (with self-care such as) washing all over or dressing',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'selfcare_disability_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Some difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Some difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'some_difficulty'
                    },
                    {
                        'labelEn': 'A lot of difficulty',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'A lot of difficulty',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'lot_difficulty'
                    },
                    {
                        'labelEn': 'Cannot do at all',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Cannot do at all',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'cannot_do'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If member has difficulty communicating, what is the severity?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If member has difficulty communicating, what is the severity?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'comms_disability_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Single',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Single',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'single'
                    },
                    {
                        'labelEn': 'Married',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Married',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'married'
                    },
                    {
                        'labelEn': 'Divorced',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Divorced',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'divorced'
                    },
                    {
                        'labelEn': 'Widowed',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Widowed',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'widowed'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If member is a child, what is her marital status?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If member is a child, what is her marital status?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'child_marital_status_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If married, age at the time of first marriage?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If married, age at the time of first marriage?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'marriage_age_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '0'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If member is a child, does he/she ever been enrolled in school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If member is a child, does he/she ever been enrolled in school?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'school_enrolled_before_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Yes',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Yes',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '1'
                    },
                    {
                        'labelEn': 'No',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'No',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': '0'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'If member is a child, does he/she currently enrolled in school',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'If member is a child, does he/she currently enrolled in school',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'school_enrolled_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                    {
                        'labelEn': 'Private',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Private',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'private'
                    },
                    {
                        'labelEn': 'Public',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Public',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'public'
                    },
                    {
                        'labelEn': 'Informal',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Informal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'informal'
                    },
                    {
                        'labelEn': 'Other',
                        'labels': [
                            {
                                'label': '',
                                'language': 'French(FR)'
                            },
                            {
                                'label': 'Other',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'other'
                    }
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'What type of school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'What type of school?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'school_type_i_f',
                'required': False,
                'type': 'SELECT_ONE'
            },
            {
                'associatedWith': '1',
                'choices': [
                ],
                'hint': "{'French(FR)': '', 'English(EN)': ''}",
                'isFlexField': True,
                'labelEn': 'How many minutes does it take for the child to go to the nearest available school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many minutes does it take for the child to go to the nearest available school?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'minutes_to_school_i_f',
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
                ],
                'hint': 'age in years',
                'isFlexField': False,
                'labelEn': 'age',
                'labels': [
                    {
                        'label': 'age',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'age',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                ],
                'hint': 'how many persons in the household',
                'isFlexField': False,
                'labelEn': 'Family Size',
                'labels': [
                    {
                        'label': 'Family Size',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'size',
                'required': True,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Household',
                'choices': [
                    {
                        'labelEn': 'Refugee',
                        'labels': [
                            {
                                'label': 'Refugee',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'REFUGEE'
                    },
                    {
                        'labelEn': 'Migrant',
                        'labels': [
                            {
                                'label': 'Migrant',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MIGRANT'
                    },
                    {
                        'labelEn': 'Citizen',
                        'labels': [
                            {
                                'label': 'Citizen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CITIZEN'
                    },
                    {
                        'labelEn': 'IDP',
                        'labels': [
                            {
                                'label': 'IDP',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IDP'
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
                'hint': 'residential status of household',
                'isFlexField': False,
                'labelEn': 'Residence Status',
                'labels': [
                    {
                        'label': 'Residence Status',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'residence_status',
                'required': True,
                'type': 'SELECT_ONE'
            }
        ]
    }
}
