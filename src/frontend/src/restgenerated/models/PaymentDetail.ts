/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeliveryMechanism } from './DeliveryMechanism';
import type { HouseholdDetail } from './HouseholdDetail';
import type { IndividualDetail } from './IndividualDetail';
import type { PaymentList } from './PaymentList';
import type { PaymentPlanDetail } from './PaymentPlanDetail';
export type PaymentDetail = {
    readonly id: string;
    unicefId?: string | null;
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
    deliveredQuantity?: string | null;
    deliveryDate?: string | null;
    deliveryType?: string | null;
    status: string;
    currency?: string | null;
    readonly fspAuthCode: string;
    hohFullName: string;
    collectorPhoneNo: string;
    collectorPhoneNoAlt: string;
    readonly verification: Record<string, any>;
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
    readonly snapshotCollectorBankAccountNumber: string | null;
    readonly snapshotCollectorBankName: string | null;
    readonly snapshotCollectorDebitCardNumber: string | null;
    readonly debitCardNumber: string;
    readonly debitCardIssuer: string;
};

