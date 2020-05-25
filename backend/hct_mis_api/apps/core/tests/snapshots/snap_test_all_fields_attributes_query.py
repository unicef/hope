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
                'labelEn': 'How many years has the child been in school?',
                'labels': [
                    {
                        'label': '',
                        'language': 'French(FR)'
                    },
                    {
                        'label': 'How many years has the child been in school?',
                        'language': 'English(EN)'
                    }
                ],
                'name': 'years_in_school_i_f',
                'required': False,
                'type': 'INTEGER'
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
                        'labelEn': 'Afghanistan',
                        'labels': [
                            {
                                'label': 'Afghanistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AF'
                    },
                    {
                        'labelEn': 'Åland Islands',
                        'labels': [
                            {
                                'label': 'Åland Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AX'
                    },
                    {
                        'labelEn': 'Albania',
                        'labels': [
                            {
                                'label': 'Albania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AL'
                    },
                    {
                        'labelEn': 'Algeria',
                        'labels': [
                            {
                                'label': 'Algeria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DZ'
                    },
                    {
                        'labelEn': 'American Samoa',
                        'labels': [
                            {
                                'label': 'American Samoa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AS'
                    },
                    {
                        'labelEn': 'Andorra',
                        'labels': [
                            {
                                'label': 'Andorra',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AD'
                    },
                    {
                        'labelEn': 'Angola',
                        'labels': [
                            {
                                'label': 'Angola',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AO'
                    },
                    {
                        'labelEn': 'Anguilla',
                        'labels': [
                            {
                                'label': 'Anguilla',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AI'
                    },
                    {
                        'labelEn': 'Antarctica',
                        'labels': [
                            {
                                'label': 'Antarctica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AQ'
                    },
                    {
                        'labelEn': 'Antigua and Barbuda',
                        'labels': [
                            {
                                'label': 'Antigua and Barbuda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AG'
                    },
                    {
                        'labelEn': 'Argentina',
                        'labels': [
                            {
                                'label': 'Argentina',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AR'
                    },
                    {
                        'labelEn': 'Armenia',
                        'labels': [
                            {
                                'label': 'Armenia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AM'
                    },
                    {
                        'labelEn': 'Aruba',
                        'labels': [
                            {
                                'label': 'Aruba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AW'
                    },
                    {
                        'labelEn': 'Australia',
                        'labels': [
                            {
                                'label': 'Australia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AU'
                    },
                    {
                        'labelEn': 'Austria',
                        'labels': [
                            {
                                'label': 'Austria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AT'
                    },
                    {
                        'labelEn': 'Azerbaijan',
                        'labels': [
                            {
                                'label': 'Azerbaijan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AZ'
                    },
                    {
                        'labelEn': 'Bahamas',
                        'labels': [
                            {
                                'label': 'Bahamas',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BS'
                    },
                    {
                        'labelEn': 'Bahrain',
                        'labels': [
                            {
                                'label': 'Bahrain',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BH'
                    },
                    {
                        'labelEn': 'Bangladesh',
                        'labels': [
                            {
                                'label': 'Bangladesh',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BD'
                    },
                    {
                        'labelEn': 'Barbados',
                        'labels': [
                            {
                                'label': 'Barbados',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BB'
                    },
                    {
                        'labelEn': 'Belarus',
                        'labels': [
                            {
                                'label': 'Belarus',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BY'
                    },
                    {
                        'labelEn': 'Belgium',
                        'labels': [
                            {
                                'label': 'Belgium',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BE'
                    },
                    {
                        'labelEn': 'Belize',
                        'labels': [
                            {
                                'label': 'Belize',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BZ'
                    },
                    {
                        'labelEn': 'Benin',
                        'labels': [
                            {
                                'label': 'Benin',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BJ'
                    },
                    {
                        'labelEn': 'Bermuda',
                        'labels': [
                            {
                                'label': 'Bermuda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BM'
                    },
                    {
                        'labelEn': 'Bhutan',
                        'labels': [
                            {
                                'label': 'Bhutan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BT'
                    },
                    {
                        'labelEn': 'Bolivia (Plurinational State of)',
                        'labels': [
                            {
                                'label': 'Bolivia (Plurinational State of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BO'
                    },
                    {
                        'labelEn': 'Bonaire, Sint Eustatius and Saba',
                        'labels': [
                            {
                                'label': 'Bonaire, Sint Eustatius and Saba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BQ'
                    },
                    {
                        'labelEn': 'Bosnia and Herzegovina',
                        'labels': [
                            {
                                'label': 'Bosnia and Herzegovina',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BA'
                    },
                    {
                        'labelEn': 'Botswana',
                        'labels': [
                            {
                                'label': 'Botswana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BW'
                    },
                    {
                        'labelEn': 'Bouvet Island',
                        'labels': [
                            {
                                'label': 'Bouvet Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BV'
                    },
                    {
                        'labelEn': 'Brazil',
                        'labels': [
                            {
                                'label': 'Brazil',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BR'
                    },
                    {
                        'labelEn': 'British Indian Ocean Territory',
                        'labels': [
                            {
                                'label': 'British Indian Ocean Territory',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IO'
                    },
                    {
                        'labelEn': 'Brunei Darussalam',
                        'labels': [
                            {
                                'label': 'Brunei Darussalam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BN'
                    },
                    {
                        'labelEn': 'Bulgaria',
                        'labels': [
                            {
                                'label': 'Bulgaria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BG'
                    },
                    {
                        'labelEn': 'Burkina Faso',
                        'labels': [
                            {
                                'label': 'Burkina Faso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BF'
                    },
                    {
                        'labelEn': 'Burundi',
                        'labels': [
                            {
                                'label': 'Burundi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BI'
                    },
                    {
                        'labelEn': 'Cabo Verde',
                        'labels': [
                            {
                                'label': 'Cabo Verde',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CV'
                    },
                    {
                        'labelEn': 'Cambodia',
                        'labels': [
                            {
                                'label': 'Cambodia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KH'
                    },
                    {
                        'labelEn': 'Cameroon',
                        'labels': [
                            {
                                'label': 'Cameroon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CM'
                    },
                    {
                        'labelEn': 'Canada',
                        'labels': [
                            {
                                'label': 'Canada',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CA'
                    },
                    {
                        'labelEn': 'Cayman Islands',
                        'labels': [
                            {
                                'label': 'Cayman Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KY'
                    },
                    {
                        'labelEn': 'Central African Republic',
                        'labels': [
                            {
                                'label': 'Central African Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CF'
                    },
                    {
                        'labelEn': 'Chad',
                        'labels': [
                            {
                                'label': 'Chad',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TD'
                    },
                    {
                        'labelEn': 'Chile',
                        'labels': [
                            {
                                'label': 'Chile',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CL'
                    },
                    {
                        'labelEn': 'China',
                        'labels': [
                            {
                                'label': 'China',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CN'
                    },
                    {
                        'labelEn': 'Christmas Island',
                        'labels': [
                            {
                                'label': 'Christmas Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CX'
                    },
                    {
                        'labelEn': 'Cocos (Keeling) Islands',
                        'labels': [
                            {
                                'label': 'Cocos (Keeling) Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CC'
                    },
                    {
                        'labelEn': 'Colombia',
                        'labels': [
                            {
                                'label': 'Colombia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CO'
                    },
                    {
                        'labelEn': 'Comoros',
                        'labels': [
                            {
                                'label': 'Comoros',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KM'
                    },
                    {
                        'labelEn': 'Congo (the Democratic Republic of the)',
                        'labels': [
                            {
                                'label': 'Congo (the Democratic Republic of the)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CD'
                    },
                    {
                        'labelEn': 'Congo',
                        'labels': [
                            {
                                'label': 'Congo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CG'
                    },
                    {
                        'labelEn': 'Cook Islands',
                        'labels': [
                            {
                                'label': 'Cook Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CK'
                    },
                    {
                        'labelEn': 'Costa Rica',
                        'labels': [
                            {
                                'label': 'Costa Rica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CR'
                    },
                    {
                        'labelEn': "Côte d'Ivoire",
                        'labels': [
                            {
                                'label': "Côte d'Ivoire",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CI'
                    },
                    {
                        'labelEn': 'Croatia',
                        'labels': [
                            {
                                'label': 'Croatia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HR'
                    },
                    {
                        'labelEn': 'Cuba',
                        'labels': [
                            {
                                'label': 'Cuba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CU'
                    },
                    {
                        'labelEn': 'Curaçao',
                        'labels': [
                            {
                                'label': 'Curaçao',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CW'
                    },
                    {
                        'labelEn': 'Cyprus',
                        'labels': [
                            {
                                'label': 'Cyprus',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CY'
                    },
                    {
                        'labelEn': 'Czechia',
                        'labels': [
                            {
                                'label': 'Czechia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CZ'
                    },
                    {
                        'labelEn': 'Denmark',
                        'labels': [
                            {
                                'label': 'Denmark',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DK'
                    },
                    {
                        'labelEn': 'Djibouti',
                        'labels': [
                            {
                                'label': 'Djibouti',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DJ'
                    },
                    {
                        'labelEn': 'Dominica',
                        'labels': [
                            {
                                'label': 'Dominica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DM'
                    },
                    {
                        'labelEn': 'Dominican Republic',
                        'labels': [
                            {
                                'label': 'Dominican Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DO'
                    },
                    {
                        'labelEn': 'Ecuador',
                        'labels': [
                            {
                                'label': 'Ecuador',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EC'
                    },
                    {
                        'labelEn': 'Egypt',
                        'labels': [
                            {
                                'label': 'Egypt',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EG'
                    },
                    {
                        'labelEn': 'El Salvador',
                        'labels': [
                            {
                                'label': 'El Salvador',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SV'
                    },
                    {
                        'labelEn': 'Equatorial Guinea',
                        'labels': [
                            {
                                'label': 'Equatorial Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GQ'
                    },
                    {
                        'labelEn': 'Eritrea',
                        'labels': [
                            {
                                'label': 'Eritrea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ER'
                    },
                    {
                        'labelEn': 'Estonia',
                        'labels': [
                            {
                                'label': 'Estonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EE'
                    },
                    {
                        'labelEn': 'Eswatini',
                        'labels': [
                            {
                                'label': 'Eswatini',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SZ'
                    },
                    {
                        'labelEn': 'Ethiopia',
                        'labels': [
                            {
                                'label': 'Ethiopia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ET'
                    },
                    {
                        'labelEn': 'Falkland Islands  [Malvinas]',
                        'labels': [
                            {
                                'label': 'Falkland Islands  [Malvinas]',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FK'
                    },
                    {
                        'labelEn': 'Faroe Islands',
                        'labels': [
                            {
                                'label': 'Faroe Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FO'
                    },
                    {
                        'labelEn': 'Fiji',
                        'labels': [
                            {
                                'label': 'Fiji',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FJ'
                    },
                    {
                        'labelEn': 'Finland',
                        'labels': [
                            {
                                'label': 'Finland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FI'
                    },
                    {
                        'labelEn': 'France',
                        'labels': [
                            {
                                'label': 'France',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FR'
                    },
                    {
                        'labelEn': 'French Guiana',
                        'labels': [
                            {
                                'label': 'French Guiana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GF'
                    },
                    {
                        'labelEn': 'French Polynesia',
                        'labels': [
                            {
                                'label': 'French Polynesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PF'
                    },
                    {
                        'labelEn': 'French Southern Territories',
                        'labels': [
                            {
                                'label': 'French Southern Territories',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TF'
                    },
                    {
                        'labelEn': 'Gabon',
                        'labels': [
                            {
                                'label': 'Gabon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GA'
                    },
                    {
                        'labelEn': 'Gambia',
                        'labels': [
                            {
                                'label': 'Gambia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GM'
                    },
                    {
                        'labelEn': 'Georgia',
                        'labels': [
                            {
                                'label': 'Georgia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GE'
                    },
                    {
                        'labelEn': 'Germany',
                        'labels': [
                            {
                                'label': 'Germany',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DE'
                    },
                    {
                        'labelEn': 'Ghana',
                        'labels': [
                            {
                                'label': 'Ghana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GH'
                    },
                    {
                        'labelEn': 'Gibraltar',
                        'labels': [
                            {
                                'label': 'Gibraltar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GI'
                    },
                    {
                        'labelEn': 'Greece',
                        'labels': [
                            {
                                'label': 'Greece',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GR'
                    },
                    {
                        'labelEn': 'Greenland',
                        'labels': [
                            {
                                'label': 'Greenland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GL'
                    },
                    {
                        'labelEn': 'Grenada',
                        'labels': [
                            {
                                'label': 'Grenada',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GD'
                    },
                    {
                        'labelEn': 'Guadeloupe',
                        'labels': [
                            {
                                'label': 'Guadeloupe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GP'
                    },
                    {
                        'labelEn': 'Guam',
                        'labels': [
                            {
                                'label': 'Guam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GU'
                    },
                    {
                        'labelEn': 'Guatemala',
                        'labels': [
                            {
                                'label': 'Guatemala',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GT'
                    },
                    {
                        'labelEn': 'Guernsey',
                        'labels': [
                            {
                                'label': 'Guernsey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GG'
                    },
                    {
                        'labelEn': 'Guinea',
                        'labels': [
                            {
                                'label': 'Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GN'
                    },
                    {
                        'labelEn': 'Guinea-Bissau',
                        'labels': [
                            {
                                'label': 'Guinea-Bissau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GW'
                    },
                    {
                        'labelEn': 'Guyana',
                        'labels': [
                            {
                                'label': 'Guyana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GY'
                    },
                    {
                        'labelEn': 'Haiti',
                        'labels': [
                            {
                                'label': 'Haiti',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HT'
                    },
                    {
                        'labelEn': 'Heard Island and McDonald Islands',
                        'labels': [
                            {
                                'label': 'Heard Island and McDonald Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HM'
                    },
                    {
                        'labelEn': 'Holy See',
                        'labels': [
                            {
                                'label': 'Holy See',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VA'
                    },
                    {
                        'labelEn': 'Honduras',
                        'labels': [
                            {
                                'label': 'Honduras',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HN'
                    },
                    {
                        'labelEn': 'Hong Kong',
                        'labels': [
                            {
                                'label': 'Hong Kong',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HK'
                    },
                    {
                        'labelEn': 'Hungary',
                        'labels': [
                            {
                                'label': 'Hungary',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HU'
                    },
                    {
                        'labelEn': 'Iceland',
                        'labels': [
                            {
                                'label': 'Iceland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IS'
                    },
                    {
                        'labelEn': 'India',
                        'labels': [
                            {
                                'label': 'India',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IN'
                    },
                    {
                        'labelEn': 'Indonesia',
                        'labels': [
                            {
                                'label': 'Indonesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ID'
                    },
                    {
                        'labelEn': 'Iran (Islamic Republic of)',
                        'labels': [
                            {
                                'label': 'Iran (Islamic Republic of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IR'
                    },
                    {
                        'labelEn': 'Iraq',
                        'labels': [
                            {
                                'label': 'Iraq',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IQ'
                    },
                    {
                        'labelEn': 'Ireland',
                        'labels': [
                            {
                                'label': 'Ireland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IE'
                    },
                    {
                        'labelEn': 'Isle of Man',
                        'labels': [
                            {
                                'label': 'Isle of Man',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IM'
                    },
                    {
                        'labelEn': 'Israel',
                        'labels': [
                            {
                                'label': 'Israel',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IL'
                    },
                    {
                        'labelEn': 'Italy',
                        'labels': [
                            {
                                'label': 'Italy',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IT'
                    },
                    {
                        'labelEn': 'Jamaica',
                        'labels': [
                            {
                                'label': 'Jamaica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JM'
                    },
                    {
                        'labelEn': 'Japan',
                        'labels': [
                            {
                                'label': 'Japan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JP'
                    },
                    {
                        'labelEn': 'Jersey',
                        'labels': [
                            {
                                'label': 'Jersey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JE'
                    },
                    {
                        'labelEn': 'Jordan',
                        'labels': [
                            {
                                'label': 'Jordan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JO'
                    },
                    {
                        'labelEn': 'Kazakhstan',
                        'labels': [
                            {
                                'label': 'Kazakhstan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KZ'
                    },
                    {
                        'labelEn': 'Kenya',
                        'labels': [
                            {
                                'label': 'Kenya',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KE'
                    },
                    {
                        'labelEn': 'Kiribati',
                        'labels': [
                            {
                                'label': 'Kiribati',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KI'
                    },
                    {
                        'labelEn': "Korea (the Democratic People's Republic of)",
                        'labels': [
                            {
                                'label': "Korea (the Democratic People's Republic of)",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KP'
                    },
                    {
                        'labelEn': 'Korea (the Republic of)',
                        'labels': [
                            {
                                'label': 'Korea (the Republic of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KR'
                    },
                    {
                        'labelEn': 'Kuwait',
                        'labels': [
                            {
                                'label': 'Kuwait',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KW'
                    },
                    {
                        'labelEn': 'Kyrgyzstan',
                        'labels': [
                            {
                                'label': 'Kyrgyzstan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KG'
                    },
                    {
                        'labelEn': "Lao People's Democratic Republic",
                        'labels': [
                            {
                                'label': "Lao People's Democratic Republic",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LA'
                    },
                    {
                        'labelEn': 'Latvia',
                        'labels': [
                            {
                                'label': 'Latvia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LV'
                    },
                    {
                        'labelEn': 'Lebanon',
                        'labels': [
                            {
                                'label': 'Lebanon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LB'
                    },
                    {
                        'labelEn': 'Lesotho',
                        'labels': [
                            {
                                'label': 'Lesotho',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LS'
                    },
                    {
                        'labelEn': 'Liberia',
                        'labels': [
                            {
                                'label': 'Liberia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LR'
                    },
                    {
                        'labelEn': 'Libya',
                        'labels': [
                            {
                                'label': 'Libya',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LY'
                    },
                    {
                        'labelEn': 'Liechtenstein',
                        'labels': [
                            {
                                'label': 'Liechtenstein',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LI'
                    },
                    {
                        'labelEn': 'Lithuania',
                        'labels': [
                            {
                                'label': 'Lithuania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LT'
                    },
                    {
                        'labelEn': 'Luxembourg',
                        'labels': [
                            {
                                'label': 'Luxembourg',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LU'
                    },
                    {
                        'labelEn': 'Macao',
                        'labels': [
                            {
                                'label': 'Macao',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MO'
                    },
                    {
                        'labelEn': 'Madagascar',
                        'labels': [
                            {
                                'label': 'Madagascar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MG'
                    },
                    {
                        'labelEn': 'Malawi',
                        'labels': [
                            {
                                'label': 'Malawi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MW'
                    },
                    {
                        'labelEn': 'Malaysia',
                        'labels': [
                            {
                                'label': 'Malaysia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MY'
                    },
                    {
                        'labelEn': 'Maldives',
                        'labels': [
                            {
                                'label': 'Maldives',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MV'
                    },
                    {
                        'labelEn': 'Mali',
                        'labels': [
                            {
                                'label': 'Mali',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ML'
                    },
                    {
                        'labelEn': 'Malta',
                        'labels': [
                            {
                                'label': 'Malta',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MT'
                    },
                    {
                        'labelEn': 'Marshall Islands',
                        'labels': [
                            {
                                'label': 'Marshall Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MH'
                    },
                    {
                        'labelEn': 'Martinique',
                        'labels': [
                            {
                                'label': 'Martinique',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MQ'
                    },
                    {
                        'labelEn': 'Mauritania',
                        'labels': [
                            {
                                'label': 'Mauritania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MR'
                    },
                    {
                        'labelEn': 'Mauritius',
                        'labels': [
                            {
                                'label': 'Mauritius',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MU'
                    },
                    {
                        'labelEn': 'Mayotte',
                        'labels': [
                            {
                                'label': 'Mayotte',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'YT'
                    },
                    {
                        'labelEn': 'Mexico',
                        'labels': [
                            {
                                'label': 'Mexico',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MX'
                    },
                    {
                        'labelEn': 'Micronesia (Federated States of)',
                        'labels': [
                            {
                                'label': 'Micronesia (Federated States of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FM'
                    },
                    {
                        'labelEn': 'Moldova (the Republic of)',
                        'labels': [
                            {
                                'label': 'Moldova (the Republic of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MD'
                    },
                    {
                        'labelEn': 'Monaco',
                        'labels': [
                            {
                                'label': 'Monaco',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MC'
                    },
                    {
                        'labelEn': 'Mongolia',
                        'labels': [
                            {
                                'label': 'Mongolia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MN'
                    },
                    {
                        'labelEn': 'Montenegro',
                        'labels': [
                            {
                                'label': 'Montenegro',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ME'
                    },
                    {
                        'labelEn': 'Montserrat',
                        'labels': [
                            {
                                'label': 'Montserrat',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MS'
                    },
                    {
                        'labelEn': 'Morocco',
                        'labels': [
                            {
                                'label': 'Morocco',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MA'
                    },
                    {
                        'labelEn': 'Mozambique',
                        'labels': [
                            {
                                'label': 'Mozambique',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MZ'
                    },
                    {
                        'labelEn': 'Myanmar',
                        'labels': [
                            {
                                'label': 'Myanmar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MM'
                    },
                    {
                        'labelEn': 'Namibia',
                        'labels': [
                            {
                                'label': 'Namibia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NA'
                    },
                    {
                        'labelEn': 'Nauru',
                        'labels': [
                            {
                                'label': 'Nauru',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NR'
                    },
                    {
                        'labelEn': 'Nepal',
                        'labels': [
                            {
                                'label': 'Nepal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NP'
                    },
                    {
                        'labelEn': 'Netherlands',
                        'labels': [
                            {
                                'label': 'Netherlands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NL'
                    },
                    {
                        'labelEn': 'New Caledonia',
                        'labels': [
                            {
                                'label': 'New Caledonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NC'
                    },
                    {
                        'labelEn': 'New Zealand',
                        'labels': [
                            {
                                'label': 'New Zealand',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NZ'
                    },
                    {
                        'labelEn': 'Nicaragua',
                        'labels': [
                            {
                                'label': 'Nicaragua',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NI'
                    },
                    {
                        'labelEn': 'Niger',
                        'labels': [
                            {
                                'label': 'Niger',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NE'
                    },
                    {
                        'labelEn': 'Nigeria',
                        'labels': [
                            {
                                'label': 'Nigeria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NG'
                    },
                    {
                        'labelEn': 'Niue',
                        'labels': [
                            {
                                'label': 'Niue',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NU'
                    },
                    {
                        'labelEn': 'Norfolk Island',
                        'labels': [
                            {
                                'label': 'Norfolk Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NF'
                    },
                    {
                        'labelEn': 'North Macedonia',
                        'labels': [
                            {
                                'label': 'North Macedonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MK'
                    },
                    {
                        'labelEn': 'Northern Mariana Islands',
                        'labels': [
                            {
                                'label': 'Northern Mariana Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MP'
                    },
                    {
                        'labelEn': 'Norway',
                        'labels': [
                            {
                                'label': 'Norway',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NO'
                    },
                    {
                        'labelEn': 'Oman',
                        'labels': [
                            {
                                'label': 'Oman',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'OM'
                    },
                    {
                        'labelEn': 'Pakistan',
                        'labels': [
                            {
                                'label': 'Pakistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PK'
                    },
                    {
                        'labelEn': 'Palau',
                        'labels': [
                            {
                                'label': 'Palau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PW'
                    },
                    {
                        'labelEn': 'Palestine, State of',
                        'labels': [
                            {
                                'label': 'Palestine, State of',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PS'
                    },
                    {
                        'labelEn': 'Panama',
                        'labels': [
                            {
                                'label': 'Panama',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PA'
                    },
                    {
                        'labelEn': 'Papua New Guinea',
                        'labels': [
                            {
                                'label': 'Papua New Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PG'
                    },
                    {
                        'labelEn': 'Paraguay',
                        'labels': [
                            {
                                'label': 'Paraguay',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PY'
                    },
                    {
                        'labelEn': 'Peru',
                        'labels': [
                            {
                                'label': 'Peru',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PE'
                    },
                    {
                        'labelEn': 'Philippines',
                        'labels': [
                            {
                                'label': 'Philippines',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PH'
                    },
                    {
                        'labelEn': 'Pitcairn',
                        'labels': [
                            {
                                'label': 'Pitcairn',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PN'
                    },
                    {
                        'labelEn': 'Poland',
                        'labels': [
                            {
                                'label': 'Poland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PL'
                    },
                    {
                        'labelEn': 'Portugal',
                        'labels': [
                            {
                                'label': 'Portugal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PT'
                    },
                    {
                        'labelEn': 'Puerto Rico',
                        'labels': [
                            {
                                'label': 'Puerto Rico',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PR'
                    },
                    {
                        'labelEn': 'Qatar',
                        'labels': [
                            {
                                'label': 'Qatar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'QA'
                    },
                    {
                        'labelEn': 'Réunion',
                        'labels': [
                            {
                                'label': 'Réunion',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RE'
                    },
                    {
                        'labelEn': 'Romania',
                        'labels': [
                            {
                                'label': 'Romania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RO'
                    },
                    {
                        'labelEn': 'Russian Federation',
                        'labels': [
                            {
                                'label': 'Russian Federation',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RU'
                    },
                    {
                        'labelEn': 'Rwanda',
                        'labels': [
                            {
                                'label': 'Rwanda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RW'
                    },
                    {
                        'labelEn': 'Saint Barthélemy',
                        'labels': [
                            {
                                'label': 'Saint Barthélemy',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BL'
                    },
                    {
                        'labelEn': 'Saint Helena, Ascension and Tristan da Cunha',
                        'labels': [
                            {
                                'label': 'Saint Helena, Ascension and Tristan da Cunha',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SH'
                    },
                    {
                        'labelEn': 'Saint Kitts and Nevis',
                        'labels': [
                            {
                                'label': 'Saint Kitts and Nevis',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KN'
                    },
                    {
                        'labelEn': 'Saint Lucia',
                        'labels': [
                            {
                                'label': 'Saint Lucia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LC'
                    },
                    {
                        'labelEn': 'Saint Martin (French part)',
                        'labels': [
                            {
                                'label': 'Saint Martin (French part)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MF'
                    },
                    {
                        'labelEn': 'Saint Pierre and Miquelon',
                        'labels': [
                            {
                                'label': 'Saint Pierre and Miquelon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PM'
                    },
                    {
                        'labelEn': 'Saint Vincent and the Grenadines',
                        'labels': [
                            {
                                'label': 'Saint Vincent and the Grenadines',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VC'
                    },
                    {
                        'labelEn': 'Samoa',
                        'labels': [
                            {
                                'label': 'Samoa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WS'
                    },
                    {
                        'labelEn': 'San Marino',
                        'labels': [
                            {
                                'label': 'San Marino',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SM'
                    },
                    {
                        'labelEn': 'Sao Tome and Principe',
                        'labels': [
                            {
                                'label': 'Sao Tome and Principe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ST'
                    },
                    {
                        'labelEn': 'Saudi Arabia',
                        'labels': [
                            {
                                'label': 'Saudi Arabia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SA'
                    },
                    {
                        'labelEn': 'Senegal',
                        'labels': [
                            {
                                'label': 'Senegal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SN'
                    },
                    {
                        'labelEn': 'Serbia',
                        'labels': [
                            {
                                'label': 'Serbia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RS'
                    },
                    {
                        'labelEn': 'Seychelles',
                        'labels': [
                            {
                                'label': 'Seychelles',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SC'
                    },
                    {
                        'labelEn': 'Sierra Leone',
                        'labels': [
                            {
                                'label': 'Sierra Leone',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SL'
                    },
                    {
                        'labelEn': 'Singapore',
                        'labels': [
                            {
                                'label': 'Singapore',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SG'
                    },
                    {
                        'labelEn': 'Sint Maarten (Dutch part)',
                        'labels': [
                            {
                                'label': 'Sint Maarten (Dutch part)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SX'
                    },
                    {
                        'labelEn': 'Slovakia',
                        'labels': [
                            {
                                'label': 'Slovakia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SK'
                    },
                    {
                        'labelEn': 'Slovenia',
                        'labels': [
                            {
                                'label': 'Slovenia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SI'
                    },
                    {
                        'labelEn': 'Solomon Islands',
                        'labels': [
                            {
                                'label': 'Solomon Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SB'
                    },
                    {
                        'labelEn': 'Somalia',
                        'labels': [
                            {
                                'label': 'Somalia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SO'
                    },
                    {
                        'labelEn': 'South Africa',
                        'labels': [
                            {
                                'label': 'South Africa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZA'
                    },
                    {
                        'labelEn': 'South Georgia and the South Sandwich Islands',
                        'labels': [
                            {
                                'label': 'South Georgia and the South Sandwich Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GS'
                    },
                    {
                        'labelEn': 'South Sudan',
                        'labels': [
                            {
                                'label': 'South Sudan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SS'
                    },
                    {
                        'labelEn': 'Spain',
                        'labels': [
                            {
                                'label': 'Spain',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ES'
                    },
                    {
                        'labelEn': 'Sri Lanka',
                        'labels': [
                            {
                                'label': 'Sri Lanka',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LK'
                    },
                    {
                        'labelEn': 'Sudan',
                        'labels': [
                            {
                                'label': 'Sudan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SD'
                    },
                    {
                        'labelEn': 'Suriname',
                        'labels': [
                            {
                                'label': 'Suriname',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SR'
                    },
                    {
                        'labelEn': 'Svalbard and Jan Mayen',
                        'labels': [
                            {
                                'label': 'Svalbard and Jan Mayen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SJ'
                    },
                    {
                        'labelEn': 'Sweden',
                        'labels': [
                            {
                                'label': 'Sweden',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SE'
                    },
                    {
                        'labelEn': 'Switzerland',
                        'labels': [
                            {
                                'label': 'Switzerland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CH'
                    },
                    {
                        'labelEn': 'Syrian Arab Republic',
                        'labels': [
                            {
                                'label': 'Syrian Arab Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SY'
                    },
                    {
                        'labelEn': 'Taiwan (Province of China)',
                        'labels': [
                            {
                                'label': 'Taiwan (Province of China)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TW'
                    },
                    {
                        'labelEn': 'Tajikistan',
                        'labels': [
                            {
                                'label': 'Tajikistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TJ'
                    },
                    {
                        'labelEn': 'Tanzania, the United Republic of',
                        'labels': [
                            {
                                'label': 'Tanzania, the United Republic of',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TZ'
                    },
                    {
                        'labelEn': 'Thailand',
                        'labels': [
                            {
                                'label': 'Thailand',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TH'
                    },
                    {
                        'labelEn': 'Timor-Leste',
                        'labels': [
                            {
                                'label': 'Timor-Leste',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TL'
                    },
                    {
                        'labelEn': 'Togo',
                        'labels': [
                            {
                                'label': 'Togo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TG'
                    },
                    {
                        'labelEn': 'Tokelau',
                        'labels': [
                            {
                                'label': 'Tokelau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TK'
                    },
                    {
                        'labelEn': 'Tonga',
                        'labels': [
                            {
                                'label': 'Tonga',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TO'
                    },
                    {
                        'labelEn': 'Trinidad and Tobago',
                        'labels': [
                            {
                                'label': 'Trinidad and Tobago',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TT'
                    },
                    {
                        'labelEn': 'Tunisia',
                        'labels': [
                            {
                                'label': 'Tunisia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TN'
                    },
                    {
                        'labelEn': 'Turkey',
                        'labels': [
                            {
                                'label': 'Turkey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TR'
                    },
                    {
                        'labelEn': 'Turkmenistan',
                        'labels': [
                            {
                                'label': 'Turkmenistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TM'
                    },
                    {
                        'labelEn': 'Turks and Caicos Islands',
                        'labels': [
                            {
                                'label': 'Turks and Caicos Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TC'
                    },
                    {
                        'labelEn': 'Tuvalu',
                        'labels': [
                            {
                                'label': 'Tuvalu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TV'
                    },
                    {
                        'labelEn': 'Uganda',
                        'labels': [
                            {
                                'label': 'Uganda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UG'
                    },
                    {
                        'labelEn': 'Ukraine',
                        'labels': [
                            {
                                'label': 'Ukraine',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UA'
                    },
                    {
                        'labelEn': 'United Arab Emirates',
                        'labels': [
                            {
                                'label': 'United Arab Emirates',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AE'
                    },
                    {
                        'labelEn': 'United Kingdom of Great Britain and Northern Ireland',
                        'labels': [
                            {
                                'label': 'United Kingdom of Great Britain and Northern Ireland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GB'
                    },
                    {
                        'labelEn': 'United States Minor Outlying Islands',
                        'labels': [
                            {
                                'label': 'United States Minor Outlying Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UM'
                    },
                    {
                        'labelEn': 'United States of America',
                        'labels': [
                            {
                                'label': 'United States of America',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'US'
                    },
                    {
                        'labelEn': 'Uruguay',
                        'labels': [
                            {
                                'label': 'Uruguay',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UY'
                    },
                    {
                        'labelEn': 'Uzbekistan',
                        'labels': [
                            {
                                'label': 'Uzbekistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UZ'
                    },
                    {
                        'labelEn': 'Vanuatu',
                        'labels': [
                            {
                                'label': 'Vanuatu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VU'
                    },
                    {
                        'labelEn': 'Venezuela (Bolivarian Republic of)',
                        'labels': [
                            {
                                'label': 'Venezuela (Bolivarian Republic of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VE'
                    },
                    {
                        'labelEn': 'Viet Nam',
                        'labels': [
                            {
                                'label': 'Viet Nam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VN'
                    },
                    {
                        'labelEn': 'Virgin Islands (British)',
                        'labels': [
                            {
                                'label': 'Virgin Islands (British)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VG'
                    },
                    {
                        'labelEn': 'Virgin Islands (U.S.)',
                        'labels': [
                            {
                                'label': 'Virgin Islands (U.S.)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VI'
                    },
                    {
                        'labelEn': 'Wallis and Futuna',
                        'labels': [
                            {
                                'label': 'Wallis and Futuna',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WF'
                    },
                    {
                        'labelEn': 'Western Sahara',
                        'labels': [
                            {
                                'label': 'Western Sahara',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EH'
                    },
                    {
                        'labelEn': 'Yemen',
                        'labels': [
                            {
                                'label': 'Yemen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'YE'
                    },
                    {
                        'labelEn': 'Zambia',
                        'labels': [
                            {
                                'label': 'Zambia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZM'
                    },
                    {
                        'labelEn': 'Zimbabwe',
                        'labels': [
                            {
                                'label': 'Zimbabwe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZW'
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
                        'labelEn': 'Afghanistan',
                        'labels': [
                            {
                                'label': 'Afghanistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AF'
                    },
                    {
                        'labelEn': 'Åland Islands',
                        'labels': [
                            {
                                'label': 'Åland Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AX'
                    },
                    {
                        'labelEn': 'Albania',
                        'labels': [
                            {
                                'label': 'Albania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AL'
                    },
                    {
                        'labelEn': 'Algeria',
                        'labels': [
                            {
                                'label': 'Algeria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DZ'
                    },
                    {
                        'labelEn': 'American Samoa',
                        'labels': [
                            {
                                'label': 'American Samoa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AS'
                    },
                    {
                        'labelEn': 'Andorra',
                        'labels': [
                            {
                                'label': 'Andorra',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AD'
                    },
                    {
                        'labelEn': 'Angola',
                        'labels': [
                            {
                                'label': 'Angola',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AO'
                    },
                    {
                        'labelEn': 'Anguilla',
                        'labels': [
                            {
                                'label': 'Anguilla',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AI'
                    },
                    {
                        'labelEn': 'Antarctica',
                        'labels': [
                            {
                                'label': 'Antarctica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AQ'
                    },
                    {
                        'labelEn': 'Antigua and Barbuda',
                        'labels': [
                            {
                                'label': 'Antigua and Barbuda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AG'
                    },
                    {
                        'labelEn': 'Argentina',
                        'labels': [
                            {
                                'label': 'Argentina',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AR'
                    },
                    {
                        'labelEn': 'Armenia',
                        'labels': [
                            {
                                'label': 'Armenia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AM'
                    },
                    {
                        'labelEn': 'Aruba',
                        'labels': [
                            {
                                'label': 'Aruba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AW'
                    },
                    {
                        'labelEn': 'Australia',
                        'labels': [
                            {
                                'label': 'Australia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AU'
                    },
                    {
                        'labelEn': 'Austria',
                        'labels': [
                            {
                                'label': 'Austria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AT'
                    },
                    {
                        'labelEn': 'Azerbaijan',
                        'labels': [
                            {
                                'label': 'Azerbaijan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AZ'
                    },
                    {
                        'labelEn': 'Bahamas',
                        'labels': [
                            {
                                'label': 'Bahamas',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BS'
                    },
                    {
                        'labelEn': 'Bahrain',
                        'labels': [
                            {
                                'label': 'Bahrain',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BH'
                    },
                    {
                        'labelEn': 'Bangladesh',
                        'labels': [
                            {
                                'label': 'Bangladesh',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BD'
                    },
                    {
                        'labelEn': 'Barbados',
                        'labels': [
                            {
                                'label': 'Barbados',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BB'
                    },
                    {
                        'labelEn': 'Belarus',
                        'labels': [
                            {
                                'label': 'Belarus',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BY'
                    },
                    {
                        'labelEn': 'Belgium',
                        'labels': [
                            {
                                'label': 'Belgium',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BE'
                    },
                    {
                        'labelEn': 'Belize',
                        'labels': [
                            {
                                'label': 'Belize',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BZ'
                    },
                    {
                        'labelEn': 'Benin',
                        'labels': [
                            {
                                'label': 'Benin',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BJ'
                    },
                    {
                        'labelEn': 'Bermuda',
                        'labels': [
                            {
                                'label': 'Bermuda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BM'
                    },
                    {
                        'labelEn': 'Bhutan',
                        'labels': [
                            {
                                'label': 'Bhutan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BT'
                    },
                    {
                        'labelEn': 'Bolivia (Plurinational State of)',
                        'labels': [
                            {
                                'label': 'Bolivia (Plurinational State of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BO'
                    },
                    {
                        'labelEn': 'Bonaire, Sint Eustatius and Saba',
                        'labels': [
                            {
                                'label': 'Bonaire, Sint Eustatius and Saba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BQ'
                    },
                    {
                        'labelEn': 'Bosnia and Herzegovina',
                        'labels': [
                            {
                                'label': 'Bosnia and Herzegovina',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BA'
                    },
                    {
                        'labelEn': 'Botswana',
                        'labels': [
                            {
                                'label': 'Botswana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BW'
                    },
                    {
                        'labelEn': 'Bouvet Island',
                        'labels': [
                            {
                                'label': 'Bouvet Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BV'
                    },
                    {
                        'labelEn': 'Brazil',
                        'labels': [
                            {
                                'label': 'Brazil',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BR'
                    },
                    {
                        'labelEn': 'British Indian Ocean Territory',
                        'labels': [
                            {
                                'label': 'British Indian Ocean Territory',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IO'
                    },
                    {
                        'labelEn': 'Brunei Darussalam',
                        'labels': [
                            {
                                'label': 'Brunei Darussalam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BN'
                    },
                    {
                        'labelEn': 'Bulgaria',
                        'labels': [
                            {
                                'label': 'Bulgaria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BG'
                    },
                    {
                        'labelEn': 'Burkina Faso',
                        'labels': [
                            {
                                'label': 'Burkina Faso',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BF'
                    },
                    {
                        'labelEn': 'Burundi',
                        'labels': [
                            {
                                'label': 'Burundi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BI'
                    },
                    {
                        'labelEn': 'Cabo Verde',
                        'labels': [
                            {
                                'label': 'Cabo Verde',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CV'
                    },
                    {
                        'labelEn': 'Cambodia',
                        'labels': [
                            {
                                'label': 'Cambodia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KH'
                    },
                    {
                        'labelEn': 'Cameroon',
                        'labels': [
                            {
                                'label': 'Cameroon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CM'
                    },
                    {
                        'labelEn': 'Canada',
                        'labels': [
                            {
                                'label': 'Canada',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CA'
                    },
                    {
                        'labelEn': 'Cayman Islands',
                        'labels': [
                            {
                                'label': 'Cayman Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KY'
                    },
                    {
                        'labelEn': 'Central African Republic',
                        'labels': [
                            {
                                'label': 'Central African Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CF'
                    },
                    {
                        'labelEn': 'Chad',
                        'labels': [
                            {
                                'label': 'Chad',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TD'
                    },
                    {
                        'labelEn': 'Chile',
                        'labels': [
                            {
                                'label': 'Chile',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CL'
                    },
                    {
                        'labelEn': 'China',
                        'labels': [
                            {
                                'label': 'China',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CN'
                    },
                    {
                        'labelEn': 'Christmas Island',
                        'labels': [
                            {
                                'label': 'Christmas Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CX'
                    },
                    {
                        'labelEn': 'Cocos (Keeling) Islands',
                        'labels': [
                            {
                                'label': 'Cocos (Keeling) Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CC'
                    },
                    {
                        'labelEn': 'Colombia',
                        'labels': [
                            {
                                'label': 'Colombia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CO'
                    },
                    {
                        'labelEn': 'Comoros',
                        'labels': [
                            {
                                'label': 'Comoros',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KM'
                    },
                    {
                        'labelEn': 'Congo (the Democratic Republic of the)',
                        'labels': [
                            {
                                'label': 'Congo (the Democratic Republic of the)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CD'
                    },
                    {
                        'labelEn': 'Congo',
                        'labels': [
                            {
                                'label': 'Congo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CG'
                    },
                    {
                        'labelEn': 'Cook Islands',
                        'labels': [
                            {
                                'label': 'Cook Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CK'
                    },
                    {
                        'labelEn': 'Costa Rica',
                        'labels': [
                            {
                                'label': 'Costa Rica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CR'
                    },
                    {
                        'labelEn': "Côte d'Ivoire",
                        'labels': [
                            {
                                'label': "Côte d'Ivoire",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CI'
                    },
                    {
                        'labelEn': 'Croatia',
                        'labels': [
                            {
                                'label': 'Croatia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HR'
                    },
                    {
                        'labelEn': 'Cuba',
                        'labels': [
                            {
                                'label': 'Cuba',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CU'
                    },
                    {
                        'labelEn': 'Curaçao',
                        'labels': [
                            {
                                'label': 'Curaçao',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CW'
                    },
                    {
                        'labelEn': 'Cyprus',
                        'labels': [
                            {
                                'label': 'Cyprus',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CY'
                    },
                    {
                        'labelEn': 'Czechia',
                        'labels': [
                            {
                                'label': 'Czechia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CZ'
                    },
                    {
                        'labelEn': 'Denmark',
                        'labels': [
                            {
                                'label': 'Denmark',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DK'
                    },
                    {
                        'labelEn': 'Djibouti',
                        'labels': [
                            {
                                'label': 'Djibouti',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DJ'
                    },
                    {
                        'labelEn': 'Dominica',
                        'labels': [
                            {
                                'label': 'Dominica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DM'
                    },
                    {
                        'labelEn': 'Dominican Republic',
                        'labels': [
                            {
                                'label': 'Dominican Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DO'
                    },
                    {
                        'labelEn': 'Ecuador',
                        'labels': [
                            {
                                'label': 'Ecuador',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EC'
                    },
                    {
                        'labelEn': 'Egypt',
                        'labels': [
                            {
                                'label': 'Egypt',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EG'
                    },
                    {
                        'labelEn': 'El Salvador',
                        'labels': [
                            {
                                'label': 'El Salvador',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SV'
                    },
                    {
                        'labelEn': 'Equatorial Guinea',
                        'labels': [
                            {
                                'label': 'Equatorial Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GQ'
                    },
                    {
                        'labelEn': 'Eritrea',
                        'labels': [
                            {
                                'label': 'Eritrea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ER'
                    },
                    {
                        'labelEn': 'Estonia',
                        'labels': [
                            {
                                'label': 'Estonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EE'
                    },
                    {
                        'labelEn': 'Eswatini',
                        'labels': [
                            {
                                'label': 'Eswatini',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SZ'
                    },
                    {
                        'labelEn': 'Ethiopia',
                        'labels': [
                            {
                                'label': 'Ethiopia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ET'
                    },
                    {
                        'labelEn': 'Falkland Islands  [Malvinas]',
                        'labels': [
                            {
                                'label': 'Falkland Islands  [Malvinas]',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FK'
                    },
                    {
                        'labelEn': 'Faroe Islands',
                        'labels': [
                            {
                                'label': 'Faroe Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FO'
                    },
                    {
                        'labelEn': 'Fiji',
                        'labels': [
                            {
                                'label': 'Fiji',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FJ'
                    },
                    {
                        'labelEn': 'Finland',
                        'labels': [
                            {
                                'label': 'Finland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FI'
                    },
                    {
                        'labelEn': 'France',
                        'labels': [
                            {
                                'label': 'France',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FR'
                    },
                    {
                        'labelEn': 'French Guiana',
                        'labels': [
                            {
                                'label': 'French Guiana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GF'
                    },
                    {
                        'labelEn': 'French Polynesia',
                        'labels': [
                            {
                                'label': 'French Polynesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PF'
                    },
                    {
                        'labelEn': 'French Southern Territories',
                        'labels': [
                            {
                                'label': 'French Southern Territories',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TF'
                    },
                    {
                        'labelEn': 'Gabon',
                        'labels': [
                            {
                                'label': 'Gabon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GA'
                    },
                    {
                        'labelEn': 'Gambia',
                        'labels': [
                            {
                                'label': 'Gambia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GM'
                    },
                    {
                        'labelEn': 'Georgia',
                        'labels': [
                            {
                                'label': 'Georgia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GE'
                    },
                    {
                        'labelEn': 'Germany',
                        'labels': [
                            {
                                'label': 'Germany',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'DE'
                    },
                    {
                        'labelEn': 'Ghana',
                        'labels': [
                            {
                                'label': 'Ghana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GH'
                    },
                    {
                        'labelEn': 'Gibraltar',
                        'labels': [
                            {
                                'label': 'Gibraltar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GI'
                    },
                    {
                        'labelEn': 'Greece',
                        'labels': [
                            {
                                'label': 'Greece',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GR'
                    },
                    {
                        'labelEn': 'Greenland',
                        'labels': [
                            {
                                'label': 'Greenland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GL'
                    },
                    {
                        'labelEn': 'Grenada',
                        'labels': [
                            {
                                'label': 'Grenada',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GD'
                    },
                    {
                        'labelEn': 'Guadeloupe',
                        'labels': [
                            {
                                'label': 'Guadeloupe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GP'
                    },
                    {
                        'labelEn': 'Guam',
                        'labels': [
                            {
                                'label': 'Guam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GU'
                    },
                    {
                        'labelEn': 'Guatemala',
                        'labels': [
                            {
                                'label': 'Guatemala',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GT'
                    },
                    {
                        'labelEn': 'Guernsey',
                        'labels': [
                            {
                                'label': 'Guernsey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GG'
                    },
                    {
                        'labelEn': 'Guinea',
                        'labels': [
                            {
                                'label': 'Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GN'
                    },
                    {
                        'labelEn': 'Guinea-Bissau',
                        'labels': [
                            {
                                'label': 'Guinea-Bissau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GW'
                    },
                    {
                        'labelEn': 'Guyana',
                        'labels': [
                            {
                                'label': 'Guyana',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GY'
                    },
                    {
                        'labelEn': 'Haiti',
                        'labels': [
                            {
                                'label': 'Haiti',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HT'
                    },
                    {
                        'labelEn': 'Heard Island and McDonald Islands',
                        'labels': [
                            {
                                'label': 'Heard Island and McDonald Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HM'
                    },
                    {
                        'labelEn': 'Holy See',
                        'labels': [
                            {
                                'label': 'Holy See',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VA'
                    },
                    {
                        'labelEn': 'Honduras',
                        'labels': [
                            {
                                'label': 'Honduras',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HN'
                    },
                    {
                        'labelEn': 'Hong Kong',
                        'labels': [
                            {
                                'label': 'Hong Kong',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HK'
                    },
                    {
                        'labelEn': 'Hungary',
                        'labels': [
                            {
                                'label': 'Hungary',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'HU'
                    },
                    {
                        'labelEn': 'Iceland',
                        'labels': [
                            {
                                'label': 'Iceland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IS'
                    },
                    {
                        'labelEn': 'India',
                        'labels': [
                            {
                                'label': 'India',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IN'
                    },
                    {
                        'labelEn': 'Indonesia',
                        'labels': [
                            {
                                'label': 'Indonesia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ID'
                    },
                    {
                        'labelEn': 'Iran (Islamic Republic of)',
                        'labels': [
                            {
                                'label': 'Iran (Islamic Republic of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IR'
                    },
                    {
                        'labelEn': 'Iraq',
                        'labels': [
                            {
                                'label': 'Iraq',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IQ'
                    },
                    {
                        'labelEn': 'Ireland',
                        'labels': [
                            {
                                'label': 'Ireland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IE'
                    },
                    {
                        'labelEn': 'Isle of Man',
                        'labels': [
                            {
                                'label': 'Isle of Man',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IM'
                    },
                    {
                        'labelEn': 'Israel',
                        'labels': [
                            {
                                'label': 'Israel',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IL'
                    },
                    {
                        'labelEn': 'Italy',
                        'labels': [
                            {
                                'label': 'Italy',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'IT'
                    },
                    {
                        'labelEn': 'Jamaica',
                        'labels': [
                            {
                                'label': 'Jamaica',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JM'
                    },
                    {
                        'labelEn': 'Japan',
                        'labels': [
                            {
                                'label': 'Japan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JP'
                    },
                    {
                        'labelEn': 'Jersey',
                        'labels': [
                            {
                                'label': 'Jersey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JE'
                    },
                    {
                        'labelEn': 'Jordan',
                        'labels': [
                            {
                                'label': 'Jordan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'JO'
                    },
                    {
                        'labelEn': 'Kazakhstan',
                        'labels': [
                            {
                                'label': 'Kazakhstan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KZ'
                    },
                    {
                        'labelEn': 'Kenya',
                        'labels': [
                            {
                                'label': 'Kenya',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KE'
                    },
                    {
                        'labelEn': 'Kiribati',
                        'labels': [
                            {
                                'label': 'Kiribati',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KI'
                    },
                    {
                        'labelEn': "Korea (the Democratic People's Republic of)",
                        'labels': [
                            {
                                'label': "Korea (the Democratic People's Republic of)",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KP'
                    },
                    {
                        'labelEn': 'Korea (the Republic of)',
                        'labels': [
                            {
                                'label': 'Korea (the Republic of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KR'
                    },
                    {
                        'labelEn': 'Kuwait',
                        'labels': [
                            {
                                'label': 'Kuwait',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KW'
                    },
                    {
                        'labelEn': 'Kyrgyzstan',
                        'labels': [
                            {
                                'label': 'Kyrgyzstan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KG'
                    },
                    {
                        'labelEn': "Lao People's Democratic Republic",
                        'labels': [
                            {
                                'label': "Lao People's Democratic Republic",
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LA'
                    },
                    {
                        'labelEn': 'Latvia',
                        'labels': [
                            {
                                'label': 'Latvia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LV'
                    },
                    {
                        'labelEn': 'Lebanon',
                        'labels': [
                            {
                                'label': 'Lebanon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LB'
                    },
                    {
                        'labelEn': 'Lesotho',
                        'labels': [
                            {
                                'label': 'Lesotho',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LS'
                    },
                    {
                        'labelEn': 'Liberia',
                        'labels': [
                            {
                                'label': 'Liberia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LR'
                    },
                    {
                        'labelEn': 'Libya',
                        'labels': [
                            {
                                'label': 'Libya',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LY'
                    },
                    {
                        'labelEn': 'Liechtenstein',
                        'labels': [
                            {
                                'label': 'Liechtenstein',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LI'
                    },
                    {
                        'labelEn': 'Lithuania',
                        'labels': [
                            {
                                'label': 'Lithuania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LT'
                    },
                    {
                        'labelEn': 'Luxembourg',
                        'labels': [
                            {
                                'label': 'Luxembourg',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LU'
                    },
                    {
                        'labelEn': 'Macao',
                        'labels': [
                            {
                                'label': 'Macao',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MO'
                    },
                    {
                        'labelEn': 'Madagascar',
                        'labels': [
                            {
                                'label': 'Madagascar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MG'
                    },
                    {
                        'labelEn': 'Malawi',
                        'labels': [
                            {
                                'label': 'Malawi',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MW'
                    },
                    {
                        'labelEn': 'Malaysia',
                        'labels': [
                            {
                                'label': 'Malaysia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MY'
                    },
                    {
                        'labelEn': 'Maldives',
                        'labels': [
                            {
                                'label': 'Maldives',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MV'
                    },
                    {
                        'labelEn': 'Mali',
                        'labels': [
                            {
                                'label': 'Mali',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ML'
                    },
                    {
                        'labelEn': 'Malta',
                        'labels': [
                            {
                                'label': 'Malta',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MT'
                    },
                    {
                        'labelEn': 'Marshall Islands',
                        'labels': [
                            {
                                'label': 'Marshall Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MH'
                    },
                    {
                        'labelEn': 'Martinique',
                        'labels': [
                            {
                                'label': 'Martinique',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MQ'
                    },
                    {
                        'labelEn': 'Mauritania',
                        'labels': [
                            {
                                'label': 'Mauritania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MR'
                    },
                    {
                        'labelEn': 'Mauritius',
                        'labels': [
                            {
                                'label': 'Mauritius',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MU'
                    },
                    {
                        'labelEn': 'Mayotte',
                        'labels': [
                            {
                                'label': 'Mayotte',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'YT'
                    },
                    {
                        'labelEn': 'Mexico',
                        'labels': [
                            {
                                'label': 'Mexico',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MX'
                    },
                    {
                        'labelEn': 'Micronesia (Federated States of)',
                        'labels': [
                            {
                                'label': 'Micronesia (Federated States of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FM'
                    },
                    {
                        'labelEn': 'Moldova (the Republic of)',
                        'labels': [
                            {
                                'label': 'Moldova (the Republic of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MD'
                    },
                    {
                        'labelEn': 'Monaco',
                        'labels': [
                            {
                                'label': 'Monaco',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MC'
                    },
                    {
                        'labelEn': 'Mongolia',
                        'labels': [
                            {
                                'label': 'Mongolia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MN'
                    },
                    {
                        'labelEn': 'Montenegro',
                        'labels': [
                            {
                                'label': 'Montenegro',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ME'
                    },
                    {
                        'labelEn': 'Montserrat',
                        'labels': [
                            {
                                'label': 'Montserrat',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MS'
                    },
                    {
                        'labelEn': 'Morocco',
                        'labels': [
                            {
                                'label': 'Morocco',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MA'
                    },
                    {
                        'labelEn': 'Mozambique',
                        'labels': [
                            {
                                'label': 'Mozambique',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MZ'
                    },
                    {
                        'labelEn': 'Myanmar',
                        'labels': [
                            {
                                'label': 'Myanmar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MM'
                    },
                    {
                        'labelEn': 'Namibia',
                        'labels': [
                            {
                                'label': 'Namibia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NA'
                    },
                    {
                        'labelEn': 'Nauru',
                        'labels': [
                            {
                                'label': 'Nauru',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NR'
                    },
                    {
                        'labelEn': 'Nepal',
                        'labels': [
                            {
                                'label': 'Nepal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NP'
                    },
                    {
                        'labelEn': 'Netherlands',
                        'labels': [
                            {
                                'label': 'Netherlands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NL'
                    },
                    {
                        'labelEn': 'New Caledonia',
                        'labels': [
                            {
                                'label': 'New Caledonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NC'
                    },
                    {
                        'labelEn': 'New Zealand',
                        'labels': [
                            {
                                'label': 'New Zealand',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NZ'
                    },
                    {
                        'labelEn': 'Nicaragua',
                        'labels': [
                            {
                                'label': 'Nicaragua',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NI'
                    },
                    {
                        'labelEn': 'Niger',
                        'labels': [
                            {
                                'label': 'Niger',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NE'
                    },
                    {
                        'labelEn': 'Nigeria',
                        'labels': [
                            {
                                'label': 'Nigeria',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NG'
                    },
                    {
                        'labelEn': 'Niue',
                        'labels': [
                            {
                                'label': 'Niue',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NU'
                    },
                    {
                        'labelEn': 'Norfolk Island',
                        'labels': [
                            {
                                'label': 'Norfolk Island',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NF'
                    },
                    {
                        'labelEn': 'North Macedonia',
                        'labels': [
                            {
                                'label': 'North Macedonia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MK'
                    },
                    {
                        'labelEn': 'Northern Mariana Islands',
                        'labels': [
                            {
                                'label': 'Northern Mariana Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MP'
                    },
                    {
                        'labelEn': 'Norway',
                        'labels': [
                            {
                                'label': 'Norway',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'NO'
                    },
                    {
                        'labelEn': 'Oman',
                        'labels': [
                            {
                                'label': 'Oman',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'OM'
                    },
                    {
                        'labelEn': 'Pakistan',
                        'labels': [
                            {
                                'label': 'Pakistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PK'
                    },
                    {
                        'labelEn': 'Palau',
                        'labels': [
                            {
                                'label': 'Palau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PW'
                    },
                    {
                        'labelEn': 'Palestine, State of',
                        'labels': [
                            {
                                'label': 'Palestine, State of',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PS'
                    },
                    {
                        'labelEn': 'Panama',
                        'labels': [
                            {
                                'label': 'Panama',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PA'
                    },
                    {
                        'labelEn': 'Papua New Guinea',
                        'labels': [
                            {
                                'label': 'Papua New Guinea',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PG'
                    },
                    {
                        'labelEn': 'Paraguay',
                        'labels': [
                            {
                                'label': 'Paraguay',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PY'
                    },
                    {
                        'labelEn': 'Peru',
                        'labels': [
                            {
                                'label': 'Peru',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PE'
                    },
                    {
                        'labelEn': 'Philippines',
                        'labels': [
                            {
                                'label': 'Philippines',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PH'
                    },
                    {
                        'labelEn': 'Pitcairn',
                        'labels': [
                            {
                                'label': 'Pitcairn',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PN'
                    },
                    {
                        'labelEn': 'Poland',
                        'labels': [
                            {
                                'label': 'Poland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PL'
                    },
                    {
                        'labelEn': 'Portugal',
                        'labels': [
                            {
                                'label': 'Portugal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PT'
                    },
                    {
                        'labelEn': 'Puerto Rico',
                        'labels': [
                            {
                                'label': 'Puerto Rico',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PR'
                    },
                    {
                        'labelEn': 'Qatar',
                        'labels': [
                            {
                                'label': 'Qatar',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'QA'
                    },
                    {
                        'labelEn': 'Réunion',
                        'labels': [
                            {
                                'label': 'Réunion',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RE'
                    },
                    {
                        'labelEn': 'Romania',
                        'labels': [
                            {
                                'label': 'Romania',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RO'
                    },
                    {
                        'labelEn': 'Russian Federation',
                        'labels': [
                            {
                                'label': 'Russian Federation',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RU'
                    },
                    {
                        'labelEn': 'Rwanda',
                        'labels': [
                            {
                                'label': 'Rwanda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RW'
                    },
                    {
                        'labelEn': 'Saint Barthélemy',
                        'labels': [
                            {
                                'label': 'Saint Barthélemy',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'BL'
                    },
                    {
                        'labelEn': 'Saint Helena, Ascension and Tristan da Cunha',
                        'labels': [
                            {
                                'label': 'Saint Helena, Ascension and Tristan da Cunha',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SH'
                    },
                    {
                        'labelEn': 'Saint Kitts and Nevis',
                        'labels': [
                            {
                                'label': 'Saint Kitts and Nevis',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'KN'
                    },
                    {
                        'labelEn': 'Saint Lucia',
                        'labels': [
                            {
                                'label': 'Saint Lucia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LC'
                    },
                    {
                        'labelEn': 'Saint Martin (French part)',
                        'labels': [
                            {
                                'label': 'Saint Martin (French part)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'MF'
                    },
                    {
                        'labelEn': 'Saint Pierre and Miquelon',
                        'labels': [
                            {
                                'label': 'Saint Pierre and Miquelon',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PM'
                    },
                    {
                        'labelEn': 'Saint Vincent and the Grenadines',
                        'labels': [
                            {
                                'label': 'Saint Vincent and the Grenadines',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VC'
                    },
                    {
                        'labelEn': 'Samoa',
                        'labels': [
                            {
                                'label': 'Samoa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WS'
                    },
                    {
                        'labelEn': 'San Marino',
                        'labels': [
                            {
                                'label': 'San Marino',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SM'
                    },
                    {
                        'labelEn': 'Sao Tome and Principe',
                        'labels': [
                            {
                                'label': 'Sao Tome and Principe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ST'
                    },
                    {
                        'labelEn': 'Saudi Arabia',
                        'labels': [
                            {
                                'label': 'Saudi Arabia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SA'
                    },
                    {
                        'labelEn': 'Senegal',
                        'labels': [
                            {
                                'label': 'Senegal',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SN'
                    },
                    {
                        'labelEn': 'Serbia',
                        'labels': [
                            {
                                'label': 'Serbia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'RS'
                    },
                    {
                        'labelEn': 'Seychelles',
                        'labels': [
                            {
                                'label': 'Seychelles',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SC'
                    },
                    {
                        'labelEn': 'Sierra Leone',
                        'labels': [
                            {
                                'label': 'Sierra Leone',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SL'
                    },
                    {
                        'labelEn': 'Singapore',
                        'labels': [
                            {
                                'label': 'Singapore',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SG'
                    },
                    {
                        'labelEn': 'Sint Maarten (Dutch part)',
                        'labels': [
                            {
                                'label': 'Sint Maarten (Dutch part)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SX'
                    },
                    {
                        'labelEn': 'Slovakia',
                        'labels': [
                            {
                                'label': 'Slovakia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SK'
                    },
                    {
                        'labelEn': 'Slovenia',
                        'labels': [
                            {
                                'label': 'Slovenia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SI'
                    },
                    {
                        'labelEn': 'Solomon Islands',
                        'labels': [
                            {
                                'label': 'Solomon Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SB'
                    },
                    {
                        'labelEn': 'Somalia',
                        'labels': [
                            {
                                'label': 'Somalia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SO'
                    },
                    {
                        'labelEn': 'South Africa',
                        'labels': [
                            {
                                'label': 'South Africa',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZA'
                    },
                    {
                        'labelEn': 'South Georgia and the South Sandwich Islands',
                        'labels': [
                            {
                                'label': 'South Georgia and the South Sandwich Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GS'
                    },
                    {
                        'labelEn': 'South Sudan',
                        'labels': [
                            {
                                'label': 'South Sudan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SS'
                    },
                    {
                        'labelEn': 'Spain',
                        'labels': [
                            {
                                'label': 'Spain',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ES'
                    },
                    {
                        'labelEn': 'Sri Lanka',
                        'labels': [
                            {
                                'label': 'Sri Lanka',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'LK'
                    },
                    {
                        'labelEn': 'Sudan',
                        'labels': [
                            {
                                'label': 'Sudan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SD'
                    },
                    {
                        'labelEn': 'Suriname',
                        'labels': [
                            {
                                'label': 'Suriname',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SR'
                    },
                    {
                        'labelEn': 'Svalbard and Jan Mayen',
                        'labels': [
                            {
                                'label': 'Svalbard and Jan Mayen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SJ'
                    },
                    {
                        'labelEn': 'Sweden',
                        'labels': [
                            {
                                'label': 'Sweden',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SE'
                    },
                    {
                        'labelEn': 'Switzerland',
                        'labels': [
                            {
                                'label': 'Switzerland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'CH'
                    },
                    {
                        'labelEn': 'Syrian Arab Republic',
                        'labels': [
                            {
                                'label': 'Syrian Arab Republic',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SY'
                    },
                    {
                        'labelEn': 'Taiwan (Province of China)',
                        'labels': [
                            {
                                'label': 'Taiwan (Province of China)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TW'
                    },
                    {
                        'labelEn': 'Tajikistan',
                        'labels': [
                            {
                                'label': 'Tajikistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TJ'
                    },
                    {
                        'labelEn': 'Tanzania, the United Republic of',
                        'labels': [
                            {
                                'label': 'Tanzania, the United Republic of',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TZ'
                    },
                    {
                        'labelEn': 'Thailand',
                        'labels': [
                            {
                                'label': 'Thailand',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TH'
                    },
                    {
                        'labelEn': 'Timor-Leste',
                        'labels': [
                            {
                                'label': 'Timor-Leste',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TL'
                    },
                    {
                        'labelEn': 'Togo',
                        'labels': [
                            {
                                'label': 'Togo',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TG'
                    },
                    {
                        'labelEn': 'Tokelau',
                        'labels': [
                            {
                                'label': 'Tokelau',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TK'
                    },
                    {
                        'labelEn': 'Tonga',
                        'labels': [
                            {
                                'label': 'Tonga',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TO'
                    },
                    {
                        'labelEn': 'Trinidad and Tobago',
                        'labels': [
                            {
                                'label': 'Trinidad and Tobago',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TT'
                    },
                    {
                        'labelEn': 'Tunisia',
                        'labels': [
                            {
                                'label': 'Tunisia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TN'
                    },
                    {
                        'labelEn': 'Turkey',
                        'labels': [
                            {
                                'label': 'Turkey',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TR'
                    },
                    {
                        'labelEn': 'Turkmenistan',
                        'labels': [
                            {
                                'label': 'Turkmenistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TM'
                    },
                    {
                        'labelEn': 'Turks and Caicos Islands',
                        'labels': [
                            {
                                'label': 'Turks and Caicos Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TC'
                    },
                    {
                        'labelEn': 'Tuvalu',
                        'labels': [
                            {
                                'label': 'Tuvalu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'TV'
                    },
                    {
                        'labelEn': 'Uganda',
                        'labels': [
                            {
                                'label': 'Uganda',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UG'
                    },
                    {
                        'labelEn': 'Ukraine',
                        'labels': [
                            {
                                'label': 'Ukraine',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UA'
                    },
                    {
                        'labelEn': 'United Arab Emirates',
                        'labels': [
                            {
                                'label': 'United Arab Emirates',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'AE'
                    },
                    {
                        'labelEn': 'United Kingdom of Great Britain and Northern Ireland',
                        'labels': [
                            {
                                'label': 'United Kingdom of Great Britain and Northern Ireland',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'GB'
                    },
                    {
                        'labelEn': 'United States Minor Outlying Islands',
                        'labels': [
                            {
                                'label': 'United States Minor Outlying Islands',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UM'
                    },
                    {
                        'labelEn': 'United States of America',
                        'labels': [
                            {
                                'label': 'United States of America',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'US'
                    },
                    {
                        'labelEn': 'Uruguay',
                        'labels': [
                            {
                                'label': 'Uruguay',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UY'
                    },
                    {
                        'labelEn': 'Uzbekistan',
                        'labels': [
                            {
                                'label': 'Uzbekistan',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'UZ'
                    },
                    {
                        'labelEn': 'Vanuatu',
                        'labels': [
                            {
                                'label': 'Vanuatu',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VU'
                    },
                    {
                        'labelEn': 'Venezuela (Bolivarian Republic of)',
                        'labels': [
                            {
                                'label': 'Venezuela (Bolivarian Republic of)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VE'
                    },
                    {
                        'labelEn': 'Viet Nam',
                        'labels': [
                            {
                                'label': 'Viet Nam',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VN'
                    },
                    {
                        'labelEn': 'Virgin Islands (British)',
                        'labels': [
                            {
                                'label': 'Virgin Islands (British)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VG'
                    },
                    {
                        'labelEn': 'Virgin Islands (U.S.)',
                        'labels': [
                            {
                                'label': 'Virgin Islands (U.S.)',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'VI'
                    },
                    {
                        'labelEn': 'Wallis and Futuna',
                        'labels': [
                            {
                                'label': 'Wallis and Futuna',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WF'
                    },
                    {
                        'labelEn': 'Western Sahara',
                        'labels': [
                            {
                                'label': 'Western Sahara',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'EH'
                    },
                    {
                        'labelEn': 'Yemen',
                        'labels': [
                            {
                                'label': 'Yemen',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'YE'
                    },
                    {
                        'labelEn': 'Zambia',
                        'labels': [
                            {
                                'label': 'Zambia',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZM'
                    },
                    {
                        'labelEn': 'Zimbabwe',
                        'labels': [
                            {
                                'label': 'Zimbabwe',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'ZW'
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
                'required': False,
                'type': 'INTEGER'
            },
            {
                'associatedWith': 'Individual',
                'choices': [
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
                        'labelEn': 'Cousin',
                        'labels': [
                            {
                                'label': 'Cousin',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'COUSIN'
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
                    {
                        'labelEn': 'Primary collector',
                        'labels': [
                            {
                                'label': 'Primary collector',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'PRIMARY'
                    },
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
                'required': False,
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
                        'labelEn': 'Female',
                        'labels': [
                            {
                                'label': 'Female',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'FEMALE'
                    }
                ],
                'hint': '',
                'isFlexField': False,
                'labelEn': 'Sex',
                'labels': [
                    {
                        'label': 'Sex',
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
                        'labelEn': 'SINGLE',
                        'labels': [
                            {
                                'label': 'SINGLE',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SINGLE'
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
                        'labelEn': 'Widow',
                        'labels': [
                            {
                                'label': 'Widow',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'WIDOW'
                    },
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
                        'labelEn': 'Separated',
                        'labels': [
                            {
                                'label': 'Separated',
                                'language': 'English(EN)'
                            }
                        ],
                        'value': 'SEPARATED'
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
                'name': 'national_id',
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
            }
        ]
    }
}
