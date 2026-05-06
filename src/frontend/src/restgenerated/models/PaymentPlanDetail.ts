/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApprovalProcess } from './ApprovalProcess';
import type { BackgroundActionStatusEnum } from './BackgroundActionStatusEnum';
import type { DeliveryMechanism } from './DeliveryMechanism';
import type { FinancialServiceProvider } from './FinancialServiceProvider';
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { PaymentPlanStatusEnum } from './PaymentPlanStatusEnum';
import type { PaymentPlanSupportingDocument } from './PaymentPlanSupportingDocument';
import type { PaymentVerificationPlan } from './PaymentVerificationPlan';
import type { ProgramCycleSmall } from './ProgramCycleSmall';
import type { ProgramSmall } from './ProgramSmall';
import type { RuleCommit } from './RuleCommit';
export type PaymentPlanDetail = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * Name
     */
    name?: string | null;
    /**
     * Status [sys]
     *
     * * `TP_OPEN` - Open
     * * `TP_LOCKED` - Locked
     * * `PROCESSING` - Processing
     * * `STEFICON_WAIT` - Steficon Wait
     * * `STEFICON_RUN` - Steficon Run
     * * `STEFICON_COMPLETED` - Steficon Completed
     * * `STEFICON_ERROR` - Steficon Error
     * * `DRAFT` - Draft
     * * `PREPARING` - Preparing
     * * `OPEN` - Open
     * * `LOCKED` - Locked
     * * `LOCKED_FSP` - Locked FSP
     * * `IN_APPROVAL` - In Approval
     * * `IN_AUTHORIZATION` - In Authorization
     * * `IN_REVIEW` - In Review
     * * `ACCEPTED` - Accepted
     * * `ABORTED` - Aborted
     * * `FINISHED` - Finished
     * * `CLOSED` - Closed
     */
    status?: PaymentPlanStatusEnum;
    /**
     * Total Households Count [sys]
     */
    totalHouseholdsCount?: number;
    /**
     * Total Individuals Count [sys]
     */
    totalIndividualsCount?: number;
    readonly currency: string | null;
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
    readonly program: ProgramSmall;
    /**
     * record revision number
     */
    version?: number;
    /**
     * Background Action Status for celery task [sys]
     *
     * * `RULE_ENGINE_RUN` - Rule Engine Running
     * * `RULE_ENGINE_ERROR` - Rule Engine Errored
     * * `XLSX_EXPORTING` - Exporting XLSX file
     * * `XLSX_EXPORT_ERROR` - Export XLSX file Error
     * * `XLSX_IMPORT_ERROR` - Import XLSX file Error
     * * `XLSX_IMPORTING_ENTITLEMENTS` - Importing Entitlements XLSX file
     * * `IMPORTING_ENTITLEMENTS` - Importing Entitlements flat amount
     * * `APPLYING_CUSTOM_EXCHANGE_RATE` - Applying Custom Exchange Rate
     * * `APPLYING_CUSTOM_EXCHANGE_RATE_ERROR` - Applying Custom Exchange Rate Error
     * * `XLSX_IMPORTING_RECONCILIATION` - Importing Reconciliation XLSX file
     * * `EXCLUDE_BENEFICIARIES` - Exclude Beneficiaries Running
     * * `EXCLUDE_BENEFICIARIES_ERROR` - Exclude Beneficiaries Error
     * * `SEND_TO_PAYMENT_GATEWAY` - Sending to Payment Gateway
     * * `SEND_TO_PAYMENT_GATEWAY_ERROR` - Send to Payment Gateway Error
     */
    backgroundActionStatus?: BackgroundActionStatusEnum | null;
    backgroundActionStatusDisplay: string;
    /**
     * Payment Plan start date
     */
    startDate?: string | null;
    /**
     * Payment Plan end date
     */
    endDate?: string | null;
    programCycle: ProgramCycleSmall;
    hasPaymentListExportFile: boolean;
    readonly hasFspDeliveryMechanismXlsxTemplate: boolean;
    importedFileName: string;
    /**
     * Imported File Date [sys]
     */
    importedFileDate?: string | null;
    readonly paymentsConflictsCount: number;
    readonly deliveryMechanism: DeliveryMechanism;
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
    readonly bankReconciliationSuccess: number;
    readonly bankReconciliationError: number;
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
    readonly isPaymentGatewayAndAllSentToFsp: boolean;
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
    /**
     * Custom Exchange Rate flag [sys]
     */
    customExchangeRate?: boolean;
    readonly unoreExchangeRate: number | null;
    readonly eligiblePaymentsCount: number;
    readonly fundsCommitments: Record<string, any> | null;
    readonly availableFundsCommitments: Array<Record<string, any>>;
    readonly paymentVerificationPlans: Array<PaymentVerificationPlan>;
    readonly adminUrl: string | null;
    /**
     * Reason for aborting
     */
    abortComment?: string;
    /**
     * Apply a fixed amount of entitlement for all payment records within a payment plan
     */
    flatAmountValue?: string | null;
};

