# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestImportedIndividualQuery::test_imported_individual_query_0_all_with_permission 1'] = {
    'data': {
        'allImportedIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1943-07-30',
                        'familyName': 'Butler',
                        'fullName': 'Benjamin Butler',
                        'givenName': 'Benjamin',
                        'phoneNo': '(953)682-4596'
                    }
                },
                {
                    'node': {
                        'birthDate': '1973-03-23',
                        'familyName': 'Torres',
                        'fullName': 'Eric Torres',
                        'givenName': 'Eric',
                        'phoneNo': '+12282315473'
                    }
                },
                {
                    'node': {
                        'birthDate': '1969-11-29',
                        'familyName': 'Franklin',
                        'fullName': 'Jenna Franklin',
                        'givenName': 'Jenna',
                        'phoneNo': '001-296-358-5428-607'
                    }
                },
                {
                    'node': {
                        'birthDate': '1946-02-15',
                        'familyName': 'Ford',
                        'fullName': 'Robin Ford',
                        'givenName': 'Robin',
                        'phoneNo': '+18663567905'
                    }
                },
                {
                    'node': {
                        'birthDate': '1983-12-21',
                        'familyName': 'Perry',
                        'fullName': 'Timothy Perry',
                        'givenName': 'Timothy',
                        'phoneNo': '(548)313-1700-902'
                    }
                }
            ]
        }
    }
}

snapshots['TestImportedIndividualQuery::test_imported_individual_query_1_all_without_permission 1'] = {
    'data': {
        'allImportedIndividuals': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allImportedIndividuals'
            ]
        }
    ]
}

snapshots['TestImportedIndividualQuery::test_imported_individual_query_2_order_by_dob_all_with_permission 1'] = {
    'data': {
        'allImportedIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1943-07-30',
                        'familyName': 'Butler',
                        'fullName': 'Benjamin Butler',
                        'givenName': 'Benjamin',
                        'phoneNo': '(953)682-4596'
                    }
                },
                {
                    'node': {
                        'birthDate': '1946-02-15',
                        'familyName': 'Ford',
                        'fullName': 'Robin Ford',
                        'givenName': 'Robin',
                        'phoneNo': '+18663567905'
                    }
                },
                {
                    'node': {
                        'birthDate': '1969-11-29',
                        'familyName': 'Franklin',
                        'fullName': 'Jenna Franklin',
                        'givenName': 'Jenna',
                        'phoneNo': '001-296-358-5428-607'
                    }
                },
                {
                    'node': {
                        'birthDate': '1973-03-23',
                        'familyName': 'Torres',
                        'fullName': 'Eric Torres',
                        'givenName': 'Eric',
                        'phoneNo': '+12282315473'
                    }
                },
                {
                    'node': {
                        'birthDate': '1983-12-21',
                        'familyName': 'Perry',
                        'fullName': 'Timothy Perry',
                        'givenName': 'Timothy',
                        'phoneNo': '(548)313-1700-902'
                    }
                }
            ]
        }
    }
}

snapshots['TestImportedIndividualQuery::test_imported_individual_query_3_order_by_dob_d_all_with_permission 1'] = {
    'data': {
        'allImportedIndividuals': {
            'edges': [
                {
                    'node': {
                        'birthDate': '1983-12-21',
                        'email': 'myemail333@mail.com',
                        'familyName': 'Perry',
                        'fullName': 'Timothy Perry',
                        'givenName': 'Timothy',
                        'phoneNo': '(548)313-1700-902'
                    }
                },
                {
                    'node': {
                        'birthDate': '1973-03-23',
                        'email': 'myemail444@mail.com',
                        'familyName': 'Torres',
                        'fullName': 'Eric Torres',
                        'givenName': 'Eric',
                        'phoneNo': '+12282315473'
                    }
                },
                {
                    'node': {
                        'birthDate': '1969-11-29',
                        'email': 'myemail555@mail.com',
                        'familyName': 'Franklin',
                        'fullName': 'Jenna Franklin',
                        'givenName': 'Jenna',
                        'phoneNo': '001-296-358-5428-607'
                    }
                },
                {
                    'node': {
                        'birthDate': '1946-02-15',
                        'email': 'myemail222@mail.com',
                        'familyName': 'Ford',
                        'fullName': 'Robin Ford',
                        'givenName': 'Robin',
                        'phoneNo': '+18663567905'
                    }
                },
                {
                    'node': {
                        'birthDate': '1943-07-30',
                        'email': 'myemail111@mail.com',
                        'familyName': 'Butler',
                        'fullName': 'Benjamin Butler',
                        'givenName': 'Benjamin',
                        'phoneNo': '(953)682-4596'
                    }
                }
            ]
        }
    }
}

snapshots['TestImportedIndividualQuery::test_imported_individual_query_single_0_with_permission 1'] = {
    'data': {
        'importedIndividual': {
            'birthDate': '1943-07-30',
            'email': 'myemail111@mail.com',
            'familyName': 'Butler',
            'fullName': 'Benjamin Butler',
            'givenName': 'Benjamin',
            'phoneNo': '(953)682-4596'
        }
    }
}

snapshots['TestImportedIndividualQuery::test_imported_individual_query_single_1_without_permission 1'] = {
    'data': {
        'importedIndividual': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'importedIndividual'
            ]
        }
    ]
}
