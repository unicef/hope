/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApprovalProcess } from './ApprovalProcess';
import type { DeliveryMechanism } from './DeliveryMechanism';
import type { DeliveryMechanismPerPaymentPlan } from './DeliveryMechanismPerPaymentPlan';
import type { FinancialServiceProvider } from './FinancialServiceProvider';
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { PaymentPlanSupportingDocument } from './PaymentPlanSupportingDocument';
import type { PaymentVerificationPlan } from './PaymentVerificationPlan';
import type { PaymentVerificationSummary } from './PaymentVerificationSummary';
import type { ProgramSmall } from './ProgramSmall';
import type { RuleCommit } from './RuleCommit';
export type PaymentPlanDetail = {
    id: string;
    unicefId?: string | null;
    /**
     * Name
     */
    name?: string | null;
    status: string;
    /**
     * Total Households Count [sys]
     */
    totalHouseholdsCount?: number;
    /**
     * Total Individuals Count [sys]
     */
    totalIndividualsCount?: number;
    currency: string;
    /**
     * Targeting level exclusion IDs
     */
    excludedIds?: string | null;
    /**
     * Total Entitled Quantity [sys]
     */
    totalEntitledQuantity?: string | null;
    /**
     * Total Delivered Quantity [sys]
     */
    totalDeliveredQuantity?: string | null;
    /**
     * Total Undelivered Quantity [sys]
     */
    totalUndeliveredQuantity?: string | null;
    /**
     * Dispersion Start Date
     */
    dispersionStartDate?: string | null;
    /**
     * Dispersion End Date
     */
    dispersionEndDate?: string | null;
    /**
     * Follow Up Payment Plan flag [sys]
     */
    isFollowUp?: boolean;
    readonly followUps: Array<FollowUpPaymentPlan>;
    readonly createdBy: string;
    readonly createdAt: string;
    readonly updatedAt: string;
    /**
     * record revision number
     */
    version?: number;
    backgroundActionStatus: string;
    /**
     * Payment Plan start date
     */
    startDate?: string | null;
    /**
     * Payment Plan end date
     */
    endDate?: string | null;
    readonly program: ProgramSmall;
    hasPaymentListExportFile: boolean;
    readonly hasFspDeliveryMechanismXlsxTemplate: boolean;
    importedFileName: string;
    /**
     * Imported File Date [sys]
     */
    importedFileDate?: string | null;
    readonly paymentsConflictsCount: number;
    readonly deliveryMechanism: DeliveryMechanism;
    readonly deliveryMechanismPerPaymentPlan: DeliveryMechanismPerPaymentPlan;
    readonly volumeByDeliveryMechanism: Record<string, any>;
    readonly splitChoices: Array<Record<string, any>>;
    /**
     * Exclusion reason (Targeting level)
     */
    exclusionReason?: string | null;
    /**
     * Exclusion reason (Targeting level) [sys]
     */
    excludeHouseholdError?: string | null;
    bankReconciliationSuccess: number;
    bankReconciliationError: number;
    canCreatePaymentVerificationPlan: boolean;
    readonly availablePaymentRecordsCount: number;
    readonly reconciliationSummary: Record<string, number>;
    readonly excludedHouseholds: Record<string, any>;
    readonly excludedIndividuals: Record<string, any>;
    readonly canCreateFollowUp: boolean;
    readonly totalWithdrawnHouseholdsCount: number;
    readonly unsuccessfulPaymentsCount: number;
    canSendToPaymentGateway: boolean;
    readonly canSplit: boolean;
    readonly supportingDocuments: Array<PaymentPlanSupportingDocument>;
    readonly totalHouseholdsCountWithValidPhoneNo: number;
    canCreateXlsxWithFspAuthCode: boolean;
    fspCommunicationChannel: string;
    readonly financialServiceProvider: FinancialServiceProvider;
    readonly canExportXlsx: boolean;
    readonly canDownloadXlsx: boolean;
    readonly canSendXlsxPassword: boolean;
    readonly approvalProcess: Array<ApprovalProcess>;
    /**
     * Total Entitled Quantity USD [sys]
     */
    totalEntitledQuantityUsd?: string | null;
    /**
     * Total Entitled Quantity Revised USD [sys]
     */
    totalEntitledQuantityRevisedUsd?: string | null;
    /**
     * Total Delivered Quantity USD [sys]
     */
    totalDeliveredQuantityUsd?: string | null;
    /**
     * Total Undelivered Quantity USD [sys]
     */
    totalUndeliveredQuantityUsd?: string | null;
    /**
     * Male Children Count [sys]
     */
    maleChildrenCount?: number;
    /**
     * Female Children Count [sys]
     */
    femaleChildrenCount?: number;
    /**
     * Male Adults Count [sys]
     */
    maleAdultsCount?: number;
    /**
     * Female Adults Count [sys]
     */
    femaleAdultsCount?: number;
    readonly steficonRule: RuleCommit;
    readonly sourcePaymentPlan: FollowUpPaymentPlan;
    /**
     * Exchange Rate [sys]
     */
    exchangeRate?: string | null;
    readonly eligiblePaymentsCount: number;
    readonly paymentVerificationSummary: PaymentVerificationSummary;
    readonly paymentVerificationPlans: Array<PaymentVerificationPlan>;
    readonly adminUrl: string;
};

