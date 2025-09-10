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
import type { PaymentStatusEnum } from './PaymentStatusEnum';
import type { PaymentVerificationDetails } from './PaymentVerificationDetails';
export type PaymentDetail = {
    readonly id: string;
    unicefId?: string | null;
    readonly householdId: string;
    householdUnicefId: string;
    householdSize: number;
    readonly householdAdmin2: string;
    readonly householdStatus: string;
    readonly hohPhoneNo: string;
    readonly hohPhoneNoAlternative: string;
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
    status?: PaymentStatusEnum;
    readonly statusDisplay: string;
    currency?: string | null;
    readonly fspAuthCode: string;
    readonly hohFullName: string;
    readonly collectorId: string;
    readonly collectorPhoneNo: string;
    readonly collectorPhoneNoAlt: string;
    readonly verification: PaymentVerificationDetails;
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

