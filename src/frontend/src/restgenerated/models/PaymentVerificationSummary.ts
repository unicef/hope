/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationPlanStatusEnum } from './PaymentVerificationPlanStatusEnum';
export type PaymentVerificationSummary = {
    readonly id: string;
    status: PaymentVerificationPlanStatusEnum;
    activationDate?: string | null;
    completionDate?: string | null;
    readonly numberOfVerificationPlans: number;
};

