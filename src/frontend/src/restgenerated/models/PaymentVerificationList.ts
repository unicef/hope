/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationPlanSmall } from './PaymentVerificationPlanSmall';
export type PaymentVerificationList = {
    readonly id: string;
    unicefId?: string | null;
    paymentVerificationPlans: PaymentVerificationPlanSmall;
    currency: string;
    /**
     * Total Delivered Quantity [sys]
     */
    totalDeliveredQuantity?: string | null;
    programCycleStartDate: string;
    programCycleEndDate: string;
    readonly updatedAt: string;
};

