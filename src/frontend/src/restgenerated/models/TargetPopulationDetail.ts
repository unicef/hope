/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeliveryMechanism } from './DeliveryMechanism';
import type { FinancialServiceProvider } from './FinancialServiceProvider';
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { ProgramCycleSmall } from './ProgramCycleSmall';
import type { ProgramSmall } from './ProgramSmall';
import type { TargetingCriteria } from './TargetingCriteria';
export type TargetPopulationDetail = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * Name
     */
    name?: string | null;
    status: string;
    /**
     * Total Households Count [sys]
     */
    totalHouseholdsCount?: number;
    /**
     * Total Individuals Count [sys]
     */
    totalIndividualsCount?: number;
    currency: string;
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
     * Follow Up Payment Plan flag [sys]
     */
    isFollowUp?: boolean;
    readonly followUps: Array<FollowUpPaymentPlan>;
    readonly createdBy: string;
    readonly createdAt: string;
    readonly updatedAt: string;
    backgroundActionStatus: string;
    /**
     * Payment Plan start date
     */
    startDate?: string | null;
    /**
     * Payment Plan end date
     */
    endDate?: string | null;
    readonly program: ProgramSmall;
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
    readonly targetingCriteria: TargetingCriteria;
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
    readonly failedWalletValidationCollectorsIds: Array<string>;
    /**
     * record revision number
     */
    version?: number;
    readonly adminUrl: string;
};

