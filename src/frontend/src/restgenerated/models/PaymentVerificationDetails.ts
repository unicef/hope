/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationPlan } from './PaymentVerificationPlan';
import type { PaymentVerificationSummary } from './PaymentVerificationSummary';
export type PaymentVerificationDetails = {
    readonly id: string;
    unicefId?: string | null;
    programName: string;
    programCycleStartDate: string;
    programCycleEndDate: string;
    readonly availablePaymentRecordsCount: number;
    readonly eligiblePaymentsCount: number;
    bankReconciliationSuccess: number;
    bankReconciliationError: number;
    canCreatePaymentVerificationPlan: boolean;
    paymentVerificationPlans: Array<PaymentVerificationPlan>;
    paymentVerificationSummary: PaymentVerificationSummary;
};

