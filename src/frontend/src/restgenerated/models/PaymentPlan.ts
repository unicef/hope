/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
export type PaymentPlan = {
    id: string;
    unicefId?: string | null;
    /**
     * Name
     */
    name?: string | null;
    status: string;
    /**
     * Target Criteria
     */
    targetingCriteria: string;
    /**
     * Total Households Count [sys]
     */
    totalHouseholdsCount?: number;
    currency: string;
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
    program: string;
    programId: string;
    readonly lastApprovalProcessDate: string | null;
    readonly lastApprovalProcessBy: string | null;
};

