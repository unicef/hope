/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationStatusEnum } from './PaymentVerificationStatusEnum';
export type PaymentVerificationDetails = {
    readonly id: string;
    receivedAmount?: string | null;
    status?: PaymentVerificationStatusEnum;
    paymentVerificationPlanUnicefId: string;
    verificationChannel: string;
    readonly adminUrl: string | null;
    /**
     * record revision number
     */
    version?: number;
    readonly isManuallyEditable: boolean;
};

