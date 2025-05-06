# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestPaymentPlanMutation::test_assign_funds_commitments_mutation 1"] = {
    "data": {"assignFundsCommitments": None},
    "errors": [
        {
            "locations": [{"column": 3, "line": 3}],
            "message": "Permission Denied: User does not have correct permission.",
            "path": ["assignFundsCommitments"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_assign_funds_commitments_mutation 2"] = {
    "data": {"assignFundsCommitments": None},
    "errors": [
        {
            "locations": [{"column": 3, "line": 3}],
            "message": "Payment plan must be in review",
            "path": ["assignFundsCommitments"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_assign_funds_commitments_mutation 3"] = {
    "data": {"assignFundsCommitments": None},
    "errors": [
        {
            "locations": [{"column": 3, "line": 3}],
            "message": "Chosen Funds Commitments are already assigned to different Payment Plan",
            "path": ["assignFundsCommitments"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_assign_funds_commitments_mutation 4"] = {
    "data": {"assignFundsCommitments": None},
    "errors": [
        {
            "locations": [{"column": 3, "line": 3}],
            "message": "Chosen Funds Commitments have wrong Business Area",
            "path": ["assignFundsCommitments"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_assign_funds_commitments_mutation 5"] = {
    "data": {"assignFundsCommitments": {"paymentPlan": {"name": "FCTP1", "status": "IN_REVIEW"}}}
}

snapshots["TestPaymentPlanMutation::test_copy_target_criteria_mutation_0_without_permission 1"] = {
    "data": {"copyTargetingCriteria": None},
    "errors": [
        {
            "locations": [{"column": 3, "line": 3}],
            "message": "Permission Denied: User does not have correct permission.",
            "path": ["copyTargetingCriteria"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_copy_target_criteria_mutation_1_with_permission 1"] = {
    "data": {"copyTargetingCriteria": None},
    "errors": [
        {
            "locations": [{"column": 3, "line": 3}],
            "message": "Not possible to assign Finished Program Cycle to Targeting",
            "path": ["copyTargetingCriteria"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_copy_target_criteria_mutation_1_with_permission 2"] = {
    "data": {"copyTargetingCriteria": None},
    "errors": [
        {
            "locations": [{"column": 3, "line": 3}],
            "message": "Payment Plan with name: New PaymentPlan and program cycle: Cycle1 already exists.",
            "path": ["copyTargetingCriteria"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_copy_target_criteria_mutation_1_with_permission 3"] = {
    "data": {
        "copyTargetingCriteria": {"paymentPlan": {"name": "Let's have One new Payment Plan XD", "status": "TP_OPEN"}}
    }
}

snapshots["TestPaymentPlanMutation::test_create_targeting_mutation_0_without_permission 1"] = {
    "data": {"createPaymentPlan": None},
    "errors": [
        {
            "locations": [{"column": 5, "line": 3}],
            "message": "Permission Denied: User does not have correct permission.",
            "path": ["createPaymentPlan"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_create_targeting_mutation_1_with_permission 1"] = {
    "data": {"createPaymentPlan": {"paymentPlan": {"name": "paymentPlanName", "status": "TP_OPEN"}}}
}

snapshots["TestPaymentPlanMutation::test_delete_payment_plan_mutation_0_without_permission 1"] = {
    "data": {"deletePaymentPlan": None},
    "errors": [
        {
            "locations": [{"column": 5, "line": 3}],
            "message": "Permission Denied: User does not have correct permission.",
            "path": ["deletePaymentPlan"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_delete_payment_plan_mutation_1_with_permission 1"] = {
    "data": {"deletePaymentPlan": {"paymentPlan": {"isRemoved": False, "name": "DeletePaymentPlan", "status": "DRAFT"}}}
}

snapshots["TestPaymentPlanMutation::test_set_steficon_target_population_mutation_0_without_permission 1"] = {
    "data": {"setSteficonRuleOnPaymentPlanPaymentList": None},
    "errors": [
        {
            "locations": [{"column": 5, "line": 3}],
            "message": "Permission Denied: User does not have correct permission.",
            "path": ["setSteficonRuleOnPaymentPlanPaymentList"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_set_steficon_target_population_mutation_1_with_permission 1"] = {
    "data": {
        "setSteficonRuleOnPaymentPlanPaymentList": {
            "paymentPlan": {"name": "TestSetSteficonTP", "status": "STEFICON_WAIT"}
        }
    }
}

snapshots["TestPaymentPlanMutation::test_update_targeting_mutation_0_without_permission 1"] = {
    "data": {"updatePaymentPlan": None},
    "errors": [
        {
            "locations": [{"column": 5, "line": 3}],
            "message": "Permission Denied: User does not have correct permission.",
            "path": ["updatePaymentPlan"],
        }
    ],
}

snapshots["TestPaymentPlanMutation::test_update_targeting_mutation_1_with_permission 1"] = {
    "data": {"updatePaymentPlan": {"paymentPlan": {"name": "NewPaymentPlanName_with_permission", "status": "TP_OPEN"}}}
}

snapshots["TestPaymentPlanMutation::test_update_targeting_mutation_2_with_tp_permission 1"] = {
    "data": {
        "updatePaymentPlan": {"paymentPlan": {"name": "NewPaymentPlanName_with_tp_permission", "status": "TP_OPEN"}}
    }
}
