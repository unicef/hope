/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeliveryMechanism } from './DeliveryMechanism';
import type { HouseholdDetail } from './HouseholdDetail';
import type { IndividualDetail } from './IndividualDetail';
import type { IndividualList } from './IndividualList';
import type { PaymentList } from './PaymentList';
import type { PaymentPlanDetail } from './PaymentPlanDetail';
export type PaymentDetail = {
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
    programName: string;
    parent: PaymentPlanDetail;
    readonly adminUrl: string;
    sourcePayment: PaymentList;
    household: HouseholdDetail;
    deliveryMechanism: DeliveryMechanism;
    collector: IndividualDetail;
    reasonForUnsuccessfulPayment?: string | null;
    /**
     * Use this field for reconciliation data
     */
    additionalDocumentNumber?: string | null;
    /**
     * Use this field for reconciliation data
     */
    additionalDocumentType?: string | null;
    /**
     * Use this field for reconciliation data when funds are collected by someone other than the designated collector or the alternate collector
     */
    additionalCollectorName?: string | null;
    transactionReferenceId?: string | null;
    readonly snapshotCollectorAccountData: any;
};

