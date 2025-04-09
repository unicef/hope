/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationStatusEnum } from './PaymentVerificationStatusEnum';
export type PaymentVerification = {
    readonly id: string;
    status?: PaymentVerificationStatusEnum;
    statusDate?: string | null;
    receivedAmount?: string | null;
};

