# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestIndividualQuery::test_individual_query_all_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1969-11-29",
                        "familyName": "Franklin",
                        "fullName": "Jenna Franklin",
                        "givenName": "Jenna",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "001-296-358-5428-607",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1973-03-23",
                        "familyName": "Torres",
                        "fullName": "Eric Torres",
                        "givenName": "Eric",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+12282315473",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1978-01-02",
                        "familyName": "Parker",
                        "fullName": "Peter Parker",
                        "givenName": "Peter",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(666)682-2345",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1946-02-15",
                        "familyName": "Ford",
                        "fullName": "Robin Ford",
                        "givenName": "Robin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+18663567905",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1965-06-26",
                        "familyName": "Bond",
                        "fullName": "James Bond",
                        "givenName": "James",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(007)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1983-12-21",
                        "familyName": "Perry",
                        "fullName": "Timothy Perry",
                        "givenName": "Timothy",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(548)313-1700-902",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_individual_query_all_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_individual_query_all_for_all_programs_area_restrictions_1 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1969-11-29",
                        "familyName": "Franklin",
                        "fullName": "Jenna Franklin",
                        "givenName": "Jenna",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "001-296-358-5428-607",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1973-03-23",
                        "familyName": "Torres",
                        "fullName": "Eric Torres",
                        "givenName": "Eric",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+12282315473",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1978-01-02",
                        "familyName": "Parker",
                        "fullName": "Peter Parker",
                        "givenName": "Peter",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(666)682-2345",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1946-02-15",
                        "familyName": "Ford",
                        "fullName": "Robin Ford",
                        "givenName": "Robin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+18663567905",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1965-06-26",
                        "familyName": "Bond",
                        "fullName": "James Bond",
                        "givenName": "James",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(007)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1983-12-21",
                        "familyName": "Perry",
                        "fullName": "Timothy Perry",
                        "givenName": "Timothy",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(548)313-1700-902",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_individual_query_all_for_all_programs_area_restrictions_2 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Test",
                        "fullName": "Tester Test",
                        "givenName": "Tester",
                        "household": {"adminArea": {"pCode": "areaother"}},
                        "phoneNo": "(953)681-4591",
                        "phoneNoValid": False,
                        "program": {"name": "Test program OTHER"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_individual_query_all_for_all_programs_permission_in_specific_programs_1 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1969-11-29",
                        "familyName": "Franklin",
                        "fullName": "Jenna Franklin",
                        "givenName": "Jenna",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "001-296-358-5428-607",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1973-03-23",
                        "familyName": "Torres",
                        "fullName": "Eric Torres",
                        "givenName": "Eric",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+12282315473",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1978-01-02",
                        "familyName": "Parker",
                        "fullName": "Peter Parker",
                        "givenName": "Peter",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(666)682-2345",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1946-02-15",
                        "familyName": "Ford",
                        "fullName": "Robin Ford",
                        "givenName": "Robin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+18663567905",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1965-06-26",
                        "familyName": "Bond",
                        "fullName": "James Bond",
                        "givenName": "James",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(007)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1983-12-21",
                        "familyName": "Perry",
                        "fullName": "Timothy Perry",
                        "givenName": "Timothy",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(548)313-1700-902",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_individual_query_all_for_all_programs_permission_in_specific_programs_2 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Test",
                        "fullName": "Tester Test",
                        "givenName": "Tester",
                        "household": {"adminArea": {"pCode": "areaother"}},
                        "phoneNo": "(953)681-4591",
                        "phoneNoValid": False,
                        "program": {"name": "Test program OTHER"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_individual_query_all_for_all_programs_permission_in_specific_programs_3 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1969-11-29",
                        "familyName": "Franklin",
                        "fullName": "Jenna Franklin",
                        "givenName": "Jenna",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "001-296-358-5428-607",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1973-03-23",
                        "familyName": "Torres",
                        "fullName": "Eric Torres",
                        "givenName": "Eric",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+12282315473",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1978-01-02",
                        "familyName": "Parker",
                        "fullName": "Peter Parker",
                        "givenName": "Peter",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(666)682-2345",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1946-02-15",
                        "familyName": "Ford",
                        "fullName": "Robin Ford",
                        "givenName": "Robin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+18663567905",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Test",
                        "fullName": "Tester Test",
                        "givenName": "Tester",
                        "household": {"adminArea": {"pCode": "areaother"}},
                        "phoneNo": "(953)681-4591",
                        "phoneNoValid": False,
                        "program": {"name": "Test program OTHER"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1965-06-26",
                        "familyName": "Bond",
                        "fullName": "James Bond",
                        "givenName": "James",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(007)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1983-12-21",
                        "familyName": "Perry",
                        "fullName": "Timothy Perry",
                        "givenName": "Timothy",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(548)313-1700-902",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_individual_query_all_for_all_programs_permission_in_whole_ba 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1969-11-29",
                        "familyName": "Franklin",
                        "fullName": "Jenna Franklin",
                        "givenName": "Jenna",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "001-296-358-5428-607",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1973-03-23",
                        "familyName": "Torres",
                        "fullName": "Eric Torres",
                        "givenName": "Eric",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+12282315473",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1978-01-02",
                        "familyName": "Parker",
                        "fullName": "Peter Parker",
                        "givenName": "Peter",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(666)682-2345",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1946-02-15",
                        "familyName": "Ford",
                        "fullName": "Robin Ford",
                        "givenName": "Robin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+18663567905",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Test",
                        "fullName": "Tester Test",
                        "givenName": "Tester",
                        "household": {"adminArea": {"pCode": "areaother"}},
                        "phoneNo": "(953)681-4591",
                        "phoneNoValid": False,
                        "program": {"name": "Test program OTHER"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1965-06-26",
                        "familyName": "Bond",
                        "fullName": "James Bond",
                        "givenName": "James",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(007)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1983-12-21",
                        "familyName": "Perry",
                        "fullName": "Timothy Perry",
                        "givenName": "Timothy",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(548)313-1700-902",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_individual_query_all_for_all_programs_user_and_partner_permissions 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1969-11-29",
                        "familyName": "Franklin",
                        "fullName": "Jenna Franklin",
                        "givenName": "Jenna",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "001-296-358-5428-607",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1973-03-23",
                        "familyName": "Torres",
                        "fullName": "Eric Torres",
                        "givenName": "Eric",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+12282315473",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1978-01-02",
                        "familyName": "Parker",
                        "fullName": "Peter Parker",
                        "givenName": "Peter",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(666)682-2345",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1946-02-15",
                        "familyName": "Ford",
                        "fullName": "Robin Ford",
                        "givenName": "Robin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+18663567905",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Test",
                        "fullName": "Tester Test",
                        "givenName": "Tester",
                        "household": {"adminArea": {"pCode": "areaother"}},
                        "phoneNo": "(953)681-4591",
                        "phoneNoValid": False,
                        "program": {"name": "Test program OTHER"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1965-06-26",
                        "familyName": "Bond",
                        "fullName": "James Bond",
                        "givenName": "James",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(007)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1983-12-21",
                        "familyName": "Perry",
                        "fullName": "Timothy Perry",
                        "givenName": "Timothy",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(548)313-1700-902",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_individual_query_all_for_all_programs_user_with_no_program_access 1"] = {
    "data": {"allIndividuals": {"edges": []}}
}

snapshots["TestIndividualQuery::test_individual_query_draft 1"] = {"data": {"allIndividuals": {"edges": []}}}

snapshots["TestIndividualQuery::test_individual_query_single_0_with_permission 1"] = {
    "data": {
        "individual": {
            "birthDate": "1943-07-30",
            "familyName": "Butler",
            "fullName": "Benjamin Butler",
            "givenName": "Benjamin",
            "phoneNo": "(953)682-4596",
        }
    }
}

snapshots["TestIndividualQuery::test_individual_query_single_1_without_permission 1"] = {
    "data": {"individual": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["individual"]}],
}

snapshots["TestIndividualQuery::test_individual_query_single_different_program_in_header 1"] = {
    "data": {"individual": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["individual"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_admin2_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1969-11-29",
                        "familyName": "Franklin",
                        "fullName": "Jenna Franklin",
                        "givenName": "Jenna",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "001-296-358-5428-607",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1973-03-23",
                        "familyName": "Torres",
                        "fullName": "Eric Torres",
                        "givenName": "Eric",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+12282315473",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1978-01-02",
                        "familyName": "Parker",
                        "fullName": "Peter Parker",
                        "givenName": "Peter",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(666)682-2345",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1946-02-15",
                        "familyName": "Ford",
                        "fullName": "Robin Ford",
                        "givenName": "Robin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+18663567905",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1965-06-26",
                        "familyName": "Bond",
                        "fullName": "James Bond",
                        "givenName": "James",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(007)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1983-12-21",
                        "familyName": "Perry",
                        "fullName": "Timothy Perry",
                        "givenName": "Timothy",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(548)313-1700-902",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                },
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_admin2_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_bank_account_number_filter_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1965-06-26",
                        "familyName": "Bond",
                        "fullName": "James Bond",
                        "givenName": "James",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(007)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_bank_account_number_filter_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_birth_certificate_filter_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1969-11-29",
                        "familyName": "Franklin",
                        "fullName": "Jenna Franklin",
                        "givenName": "Jenna",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "001-296-358-5428-607",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_birth_certificate_filter_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_disability_card_filter_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1978-01-02",
                        "familyName": "Parker",
                        "fullName": "Peter Parker",
                        "givenName": "Peter",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(666)682-2345",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_disability_card_filter_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_drivers_license_filter_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_drivers_license_filter_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_full_name_filter_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1969-11-29",
                        "familyName": "Franklin",
                        "fullName": "Jenna Franklin",
                        "givenName": "Jenna",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "001-296-358-5428-607",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_full_name_filter_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_national_id_filter_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_national_id_filter_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_national_passport_filter_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1946-02-15",
                        "familyName": "Ford",
                        "fullName": "Robin Ford",
                        "givenName": "Robin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "+18663567905",
                        "phoneNoValid": True,
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_national_passport_filter_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_phone_no_filter_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1943-07-30",
                        "familyName": "Butler",
                        "fullName": "Benjamin Butler",
                        "givenName": "Benjamin",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(953)682-4596",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_phone_no_filter_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_tax_id_filter_0_with_permission 1"] = {
    "data": {
        "allIndividuals": {
            "edges": [
                {
                    "node": {
                        "birthDate": "1983-12-21",
                        "familyName": "Perry",
                        "fullName": "Timothy Perry",
                        "givenName": "Timothy",
                        "household": {"adminArea": {"pCode": "area2"}},
                        "phoneNo": "(548)313-1700-902",
                        "phoneNoValid": False,
                        "program": {"name": "Test program ONE"},
                    }
                }
            ]
        }
    }
}

snapshots["TestIndividualQuery::test_query_individuals_by_search_tax_id_filter_1_without_permission 1"] = {
    "data": {"allIndividuals": None},
    "errors": [{"locations": [{"column": 7, "line": 3}], "message": "Permission Denied", "path": ["allIndividuals"]}],
}

snapshots[
    "TestIndividualWithDeliveryMechanismsDataQuery::test_individual_query_delivery_mechanisms_data_0_with_permissions 1"
] = {
    "data": {
        "individual": {
            "birthDate": "1943-07-30",
            "deliveryMechanismsData": [
                {
                    "individualTabData": '{"card_number__atm_card": "123", "card_expiry_date__atm_card": "2022-01-01", "name_of_cardholder__atm_card": "Marek"}',
                    "isValid": True,
                    "name": "ATM Card",
                },
                {
                    "individualTabData": '{"delivery_phone_number__mobile_money": "123456789", "provider__mobile_money": "Provider", "service_provider_code__mobile_money": "ABC"}',
                    "isValid": False,
                    "name": "Mobile Money",
                },
            ],
            "familyName": "Butler",
            "fullName": "Benjamin Butler",
            "givenName": "Benjamin",
            "phoneNo": "(953)682-4596",
        }
    }
}

snapshots[
    "TestIndividualWithDeliveryMechanismsDataQuery::test_individual_query_delivery_mechanisms_data_1_without_permissions 1"
] = {
    "data": {
        "individual": {
            "birthDate": "1943-07-30",
            "deliveryMechanismsData": [],
            "familyName": "Butler",
            "fullName": "Benjamin Butler",
            "givenName": "Benjamin",
            "phoneNo": "(953)682-4596",
        }
    }
}

snapshots["TestIndividualWithFlexFieldsQuery::test_individual_query_single_with_flex_fields 1"] = {
    "data": {
        "individual": {
            "birthDate": "1943-07-30",
            "familyName": "Butler",
            "flexFields": {
                "pdu_field_1": {
                    "1": {"collection_date": "2021-01-01", "value": 123.45},
                    "2": {"collection_date": "2021-01-01", "value": 234.56},
                },
                "pdu_field_2": {"4": {"collection_date": "2021-01-01", "value": "Value D"}},
            },
            "fullName": "Benjamin Butler",
            "givenName": "Benjamin",
            "phoneNo": "(953)682-4596",
        }
    }
}
