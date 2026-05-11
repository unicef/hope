/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentPlanStatusEnum } from './PaymentPlanStatusEnum';
import type { PlanTypeEnum } from './PlanTypeEnum';
export type FollowUpPaymentPlan = {
    readonly id: string;
    unicefId?: string | null;
    status: PaymentPlanStatusEnum;
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
    /**
     * Name
     */
    name?: string | null;
};

