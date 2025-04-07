/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PaymentList = {
    id: string;
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
};

