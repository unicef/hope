/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationPlan } from './PaymentVerificationPlan';
import type { PaymentVerificationSummary } from './PaymentVerificationSummary';
export type PaymentVerificationPlanDetails = {
    readonly id: string;
    unicefId?: string | null;
    programName: string;
    programId: string;
    programCycleStartDate: string;
    programCycleEndDate: string;
    readonly availablePaymentRecordsCount: number;
    readonly eligiblePaymentsCount: number;
    bankReconciliationSuccess: number;
    bankReconciliationError: number;
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
     * Follow Up Payment Plan flag [sys]
     */
    isFollowUp?: boolean;
    /**
     * record revision number
     */
    version?: number;
};

