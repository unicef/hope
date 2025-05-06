# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestAdjudicationTicketPartnerPermission::test_close_ticket_when_partner_does_not_have_permission 1"] = {
    "data": {"grievanceStatusChange": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 3}],
            "message": "Permission Denied: User does not have access to close ticket",
            "path": ["grievanceStatusChange"],
        }
    ],
}

snapshots["TestAdjudicationTicketPartnerPermission::test_close_ticket_when_partner_is_unicef 1"] = {
    "data": {
        "grievanceStatusChange": {
            "__typename": "GrievanceStatusChangeMutation",
            "grievanceTicket": {"__typename": "GrievanceTicketNode", "description": "GrievanceTicket", "status": 6},
        }
    }
}

snapshots["TestAdjudicationTicketPartnerPermission::test_close_ticket_when_partner_with_permission 1"] = {
    "data": {
        "grievanceStatusChange": {
            "__typename": "GrievanceStatusChangeMutation",
            "grievanceTicket": {"__typename": "GrievanceTicketNode", "description": "GrievanceTicket", "status": 6},
        }
    }
}

snapshots[
    "TestAdjudicationTicketPartnerPermission::test_close_ticket_when_partner_with_permission_and_no_selected_program 1"
] = {
    "data": {
        "grievanceStatusChange": {
            "__typename": "GrievanceStatusChangeMutation",
            "grievanceTicket": {"__typename": "GrievanceTicketNode", "description": "GrievanceTicket", "status": 6},
        }
    }
}

snapshots["TestAdjudicationTicketPartnerPermission::test_select_individual_when_partner_does_not_have_permission 1"] = {
    "data": {"approveNeedsAdjudication": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 8}],
            "message": "Permission Denied: User does not have access to select individual",
            "path": ["approveNeedsAdjudication"],
        }
    ],
}

snapshots["TestAdjudicationTicketPartnerPermission::test_select_individual_when_partner_is_unicef 1"] = {
    "data": {
        "approveNeedsAdjudication": {
            "__typename": "NeedsAdjudicationApproveMutation",
            "grievanceTicket": {"__typename": "GrievanceTicketNode", "description": "GrievanceTicket", "status": 5},
        }
    }
}

snapshots["TestAdjudicationTicketPartnerPermission::test_select_individual_when_partner_with_permission 1"] = {
    "data": {
        "approveNeedsAdjudication": {
            "__typename": "NeedsAdjudicationApproveMutation",
            "grievanceTicket": {"__typename": "GrievanceTicketNode", "description": "GrievanceTicket", "status": 5},
        }
    }
}

snapshots[
    "TestAdjudicationTicketPartnerPermission::test_select_individual_when_partner_with_permission_and_no_selected_program 1"
] = {
    "data": {
        "approveNeedsAdjudication": {
            "__typename": "NeedsAdjudicationApproveMutation",
            "grievanceTicket": {"__typename": "GrievanceTicketNode", "description": "GrievanceTicket", "status": 5},
        }
    }
}

snapshots[
    "TestAdjudicationTicketPartnerPermission::test_select_individual_when_partner_with_permission_with_selectedIndividualId 1"
] = {
    "data": {
        "approveNeedsAdjudication": {
            "__typename": "NeedsAdjudicationApproveMutation",
            "grievanceTicket": {"__typename": "GrievanceTicketNode", "description": "GrievanceTicket", "status": 5},
        }
    }
}

snapshots[
    "TestAdjudicationTicketPartnerPermission::test_select_individual_when_partner_with_permission_with_selectedIndividualId_incorrect 1"
] = {
    "data": {"approveNeedsAdjudication": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 8}],
            "message": "['The selected individual IND-111 is not valid, must be one of those attached to the ticket']",
            "path": ["approveNeedsAdjudication"],
        }
    ],
}

snapshots[
    "TestAdjudicationTicketPartnerPermission::test_select_individual_when_partner_with_permission_with_selected_individual_and_selected_individuals 1"
] = {
    "data": {"approveNeedsAdjudication": None},
    "errors": [
        {
            "locations": [{"column": 7, "line": 8}],
            "message": "Only one option for duplicate or distinct or clear individuals is available",
            "path": ["approveNeedsAdjudication"],
        }
    ],
}
