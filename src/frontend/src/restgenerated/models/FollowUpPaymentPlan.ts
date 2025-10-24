/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentPlanStatusEnum } from './PaymentPlanStatusEnum';
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
     * Follow Up Payment Plan flag [sys]
     */
    isFollowUp?: boolean;
    /**
     * Name
     */
    name?: string | null;
};

