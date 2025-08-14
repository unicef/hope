/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationDetailsStatusEnum } from './PaymentVerificationDetailsStatusEnum';
export type PaymentVerificationDetails = {
    readonly id: string;
    receivedAmount?: string | null;
    status?: PaymentVerificationDetailsStatusEnum;
    paymentVerificationPlanUnicefId: string;
    verificationChannel: string;
    readonly adminUrl: string;
    /**
     * record revision number
     */
    version?: number;
    readonly isManuallyEditable: boolean;
};

