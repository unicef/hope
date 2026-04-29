/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationPlan } from './PaymentVerificationPlan';
import type { PaymentVerificationSummary } from './PaymentVerificationSummary';
import type { PlanTypeEnum } from './PlanTypeEnum';
export type PaymentVerificationPlanDetails = {
    readonly id: string;
    unicefId?: string | null;
    programName: string;
    programId: string;
    programCycleStartDate: string;
    programCycleEndDate: string;
    readonly availablePaymentRecordsCount: number;
    readonly eligiblePaymentsCount: number;
    readonly bankReconciliationSuccess: number;
    readonly bankReconciliationError: number;
    canCreatePaymentVerificationPlan: boolean;
    paymentVerificationPlans: Array<PaymentVerificationPlan>;
    paymentVerificationSummary: PaymentVerificationSummary;
    /**
     * Payment Plan start date
     */
    startDate?: string | null;
    /**
     * Payment Plan end date
     */
    endDate?: string | null;
    /**
     * Payment Plan type [sys]
     *
     * * `REGULAR` - Regular
     * * `TOP_UP` - Top Up
     * * `FOLLOW_UP` - Follow Up
     */
    planType?: PlanTypeEnum;
    /**
     * record revision number
     */
    version?: number;
};

