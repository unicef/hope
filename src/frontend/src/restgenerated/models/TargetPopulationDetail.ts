/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BuildStatusEnum } from './BuildStatusEnum';
import type { DeliveryMechanism } from './DeliveryMechanism';
import type { FinancialServiceProvider } from './FinancialServiceProvider';
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { PaymentPlanBackgroundActionStatusEnum } from './PaymentPlanBackgroundActionStatusEnum';
import type { PaymentPlanStatusEnum } from './PaymentPlanStatusEnum';
import type { PlanTypeEnum } from './PlanTypeEnum';
import type { ProgramCycleSmall } from './ProgramCycleSmall';
import type { ProgramSmall } from './ProgramSmall';
import type { RuleCommit } from './RuleCommit';
import type { TargetingCriteriaRule } from './TargetingCriteriaRule';
export type TargetPopulationDetail = {
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
    /**
     * Total Households Count [sys]
     */
    totalHouseholdsCount?: number;
    /**
     * Total Individuals Count [sys]
     */
    totalIndividualsCount?: number;
    readonly currency: string | null;
    /**
     * Targeting level exclusion IDs
     */
    excludedIds?: string | null;
    /**
     * Total Entitled Quantity [sys]
     */
    totalEntitledQuantity?: string | null;
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
    readonly createdBy: string;
    readonly createdAt: string;
    readonly updatedAt: string;
    readonly program: ProgramSmall;
    backgroundActionStatus: PaymentPlanBackgroundActionStatusEnum;
    /**
     * Payment Plan start date
     */
    startDate?: string | null;
    /**
     * Payment Plan end date
     */
    endDate?: string | null;
    programCycle: ProgramCycleSmall;
    /**
     * Exclusion reason (Targeting level)
     */
    exclusionReason?: string | null;
    /**
     * Male Children Count [sys]
     */
    maleChildrenCount?: number;
    /**
     * Female Children Count [sys]
     */
    femaleChildrenCount?: number;
    /**
     * Male Adults Count [sys]
     */
    maleAdultsCount?: number;
    /**
     * Female Adults Count [sys]
     */
    femaleAdultsCount?: number;
    readonly rules: Array<TargetingCriteriaRule>;
    readonly steficonRuleTargeting: RuleCommit;
    /**
     * Written by a tool such as Engine Formula
     */
    vulnerabilityScoreMin?: string | null;
    /**
     * Written by a tool such as Engine Formula
     */
    vulnerabilityScoreMax?: string | null;
    readonly deliveryMechanism: DeliveryMechanism;
    readonly financialServiceProvider: FinancialServiceProvider;
    readonly failedWalletValidationCollectorsIds: Array<string | null>;
    /**
     * record revision number
     */
    version?: number;
    readonly adminUrl: string | null;
    readonly screenBeneficiary: boolean;
    /**
     * Exclude households with individuals (members or collectors) on sanction list.
     */
    flagExcludeIfOnSanctionList?: boolean;
    /**
     * Exclude households with individuals (members or collectors) that have active adjudication ticket(s).
     */
    flagExcludeIfActiveAdjudicationTicket?: boolean;
    /**
     * Build Status for celery task [sys]
     *
     * * `PENDING` - Pending
     * * `BUILDING` - Building
     * * `FAILED` - Failed
     * * `OK` - Ok
     */
    buildStatus?: BuildStatusEnum | null;
};

