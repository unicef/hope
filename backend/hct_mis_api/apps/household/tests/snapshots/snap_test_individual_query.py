# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestIndividualQuery::test_individual_query_all 1'] = {
    'data': {
        'allIndividuals': {
            'edges': [
                {
                    'node': {
                        'dob': '1943-07-30',
                        'firstName': 'Benjamin',
                        'fullName': 'Benjamin Butler',
                        'lastName': 'Butler',
                        'phoneNumber': '(953)682-4596'
                    }
                },
                {
                    'node': {
                        'dob': '1946-02-15',
                        'firstName': 'Robin',
                        'fullName': 'Robin Ford',
                        'lastName': 'Ford',
                        'phoneNumber': '+18663567905'
                    }
                },
                {
                    'node': {
                        'dob': '1983-12-21',
                        'firstName': 'Timothy',
                        'fullName': 'Timothy Perry',
                        'lastName': 'Perry',
                        'phoneNumber': '(548)313-1700-902'
                    }
                },
                {
                    'node': {
                        'dob': '1973-03-23',
                        'firstName': 'Eric',
                        'fullName': 'Eric Torres',
                        'lastName': 'Torres',
                        'phoneNumber': '(228)231-5473'
                    }
                },
                {
                    'node': {
                        'dob': '1969-11-29',
                        'firstName': 'Jenna',
                        'fullName': 'Jenna Franklin',
                        'lastName': 'Franklin',
                        'phoneNumber': '001-296-358-5428-607'
                    }
                }
            ]
        }
    }
}

snapshots['TestIndividualQuery::test_individual_query_single 1'] = {
    'data': {
        'individual': {
            'dob': '1943-07-30',
            'firstName': 'Benjamin',
            'fullName': 'Benjamin Butler',
            'lastName': 'Butler',
            'phoneNumber': '(953)682-4596'
        }
    }
}
