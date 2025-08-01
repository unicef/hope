/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationSummaryStatusEnum } from './PaymentVerificationSummaryStatusEnum';
export type PaymentVerificationSummary = {
    readonly id: string;
    status?: PaymentVerificationSummaryStatusEnum;
    activationDate?: string | null;
    completionDate?: string | null;
    readonly numberOfVerificationPlans: number;
    statusDisplay: string;
};

