/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { PaymentVerification } from './PaymentVerification';
export type PaymentDetail = {
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
    status: string;
    readonly fspAuthCode: string;
    parent: FollowUpPaymentPlan;
    paymentVerifications: PaymentVerification;
    readonly adminUrl: string;
};

