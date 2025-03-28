/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PaymentList = {
    id: string;
    unicef_id?: string | null;
    household_unicef_id: string;
    household_size: number;
    readonly household_admin2: string;
    /**
     * Get from Household Snapshot
     */
    readonly snapshot_collector_full_name: any;
    readonly fsp_name: string;
    entitlement_quantity?: string | null;
    delivered_quantity?: string | null;
    status: string;
    readonly fsp_auth_code: string;
};

