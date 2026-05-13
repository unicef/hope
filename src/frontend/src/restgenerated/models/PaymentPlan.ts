/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { PaymentPlanStatusEnum } from './PaymentPlanStatusEnum';
import type { PlanTypeEnum } from './PlanTypeEnum';
export type PaymentPlan = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * Name
     */
    name?: string | null;
    /**
     * Status [sys]
     *
     * * `TP_OPEN` - Open
     * * `TP_LOCKED` - Locked
     * * `PROCESSING` - Processing
     * * `STEFICON_WAIT` - Steficon Wait
     * * `STEFICON_RUN` - Steficon Run
     * * `STEFICON_COMPLETED` - Steficon Completed
     * * `STEFICON_ERROR` - Steficon Error
     * * `DRAFT` - Draft
     * * `PREPARING` - Preparing
     * * `OPEN` - Open
     * * `LOCKED` - Locked
     * * `LOCKED_FSP` - Locked FSP
     * * `IN_APPROVAL` - In Approval
     * * `IN_AUTHORIZATION` - In Authorization
     * * `IN_REVIEW` - In Review
     * * `ACCEPTED` - Accepted
     * * `ABORTED` - Aborted
     * * `FINISHED` - Finished
     * * `CLOSED` - Closed
     */
    status?: PaymentPlanStatusEnum;
    statusDisplay: string;
    /**
     * Total Households Count [sys]
     */
    totalHouseholdsCount?: number;
    readonly currency: string | null;
    /**
     * Total Entitled Quantity [sys]
     */
    totalEntitledQuantity?: string | null;
    /**
     * Total Entitled Quantity USD [sys]
     */
    totalEntitledQuantityUsd?: string | null;
    /**
     * Total Delivered Quantity [sys]
     */
    totalDeliveredQuantity?: string | null;
    /**
     * Total Undelivered Quantity [sys]
     */
    totalUndeliveredQuantity?: string | null;
    /**
     * Dispersion Start Date
     */
    dispersionStartDate?: string | null;
    /**
     * Dispersion End Date
     */
    dispersionEndDate?: string | null;
    /**
     * Payment Plan type [sys]
     *
     * * `REGULAR` - Regular
     * * `TOP_UP` - Top Up
     * * `FOLLOW_UP` - Follow Up
     */
    planType?: PlanTypeEnum;
    readonly followUps: Array<FollowUpPaymentPlan>;
    readonly topUps: Array<FollowUpPaymentPlan>;
    program: string;
    readonly programId: string;
    readonly programCode: string;
    readonly programCycleId: string;
    readonly lastApprovalProcessDate: string | null;
    readonly lastApprovalProcessBy: string | null;
    readonly adminUrl: string | null;
    readonly screenBeneficiary: boolean;
    readonly hasPaymentsReconciliationOverdue: boolean;
};

