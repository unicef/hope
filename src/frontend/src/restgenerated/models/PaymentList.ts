/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationDetails } from './PaymentVerificationDetails';
export type PaymentList = {
    readonly id: string;
    unicefId?: string | null;
    householdUnicefId: string;
    householdSize: number;
    readonly householdAdmin2: string;
    /**
     * Get from Household Snapshot
     */
    readonly snapshotCollectorFullName: any;
    readonly fspName: string;
    entitlementQuantity?: string | null;
    deliveredQuantity?: string | null;
    deliveryDate?: string | null;
    deliveryType?: string | null;
    status: string;
    currency?: string | null;
    readonly fspAuthCode: string;
    hohFullName: string;
    collectorPhoneNo: string;
    collectorPhoneNoAlt: string;
    paymentVerifications: Array<PaymentVerificationDetails>;
};

