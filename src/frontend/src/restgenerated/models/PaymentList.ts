/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { IndividualList } from './IndividualList';
export type PaymentList = {
    readonly id: string;
    unicefId?: string | null;
    readonly householdId: string;
    householdUnicefId: string;
    householdSize: number;
    readonly householdAdmin2: string;
    readonly householdStatus: string;
    hohPhoneNo: string;
    hohPhoneNoAlternative: string;
    /**
     * Get from Household Snapshot
     */
    readonly snapshotCollectorFullName: any;
    readonly fspName: string;
    entitlementQuantity?: string | null;
    entitlementQuantityUsd?: string | null;
    deliveredQuantity?: string | null;
    deliveredQuantityUsd?: string | null;
    deliveryDate?: string | null;
    deliveryType?: string | null;
    status: string;
    currency?: string | null;
    readonly fspAuthCode: string;
    hohFullName: string;
    readonly collectorId: string;
    collectorPhoneNo: string;
    collectorPhoneNoAlt: string;
    readonly verification: Record<string, any>;
    readonly paymentPlanHardConflicted: boolean;
    readonly paymentPlanHardConflictedData: Array<any>;
    readonly paymentPlanSoftConflicted: boolean;
    readonly paymentPlanSoftConflictedData: Array<any>;
    readonly peopleIndividual: IndividualList;
};

