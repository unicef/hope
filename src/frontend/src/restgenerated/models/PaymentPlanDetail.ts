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
import type { Rule } from './Rule';
export type PaymentPlanDetail = {
    id: string;
    unicef_id?: string | null;
    /**
     * Name
     */
    name?: string | null;
    status: string;
    /**
     * Total Households Count [sys]
     */
    total_households_count?: number;
    /**
     * Total Individuals Count [sys]
     */
    total_individuals_count?: number;
    currency: string;
    /**
     * Targeting level exclusion IDs
     */
    excluded_ids?: string | null;
    /**
     * Total Entitled Quantity [sys]
     */
    total_entitled_quantity?: string | null;
    /**
     * Total Delivered Quantity [sys]
     */
    total_delivered_quantity?: string | null;
    /**
     * Total Undelivered Quantity [sys]
     */
    total_undelivered_quantity?: string | null;
    /**
     * Dispersion Start Date
     */
    dispersion_start_date?: string | null;
    /**
     * Dispersion End Date
     */
    dispersion_end_date?: string | null;
    /**
     * Follow Up Payment Plan flag [sys]
     */
    is_follow_up?: boolean;
    readonly follow_ups: Array<FollowUpPaymentPlan>;
    readonly created_by: string;
    readonly created_at: string;
    readonly updated_at: string;
    /**
     * record revision number
     */
    version?: number;
    background_action_status: string;
    /**
     * Payment Plan start date
     */
    start_date?: string | null;
    /**
     * Payment Plan end date
     */
    end_date?: string | null;
    readonly program: ProgramSmall;
    has_payment_list_export_file: boolean;
    readonly has_fsp_delivery_mechanism_xlsx_template: boolean;
    imported_file_name: string;
    /**
     * Imported File Date [sys]
     */
    imported_file_date?: string | null;
    readonly payments_conflicts_count: number;
    readonly delivery_mechanism: DeliveryMechanism;
    readonly delivery_mechanism_per_payment_plan: DeliveryMechanismPerPaymentPlan;
    readonly volume_by_delivery_mechanism: Record<string, any>;
    readonly split_choices: Array<Record<string, any>>;
    /**
     * Exclusion reason (Targeting level)
     */
    exclusion_reason?: string | null;
    /**
     * Exclusion reason (Targeting level) [sys]
     */
    exclude_household_error?: string | null;
    bank_reconciliation_success: number;
    bank_reconciliation_error: number;
    can_create_payment_verification_plan: boolean;
    readonly available_payment_records_count: number;
    readonly reconciliation_summary: Record<string, number>;
    readonly excluded_households: Record<string, any>;
    readonly excluded_individuals: Record<string, any>;
    readonly can_create_follow_up: boolean;
    readonly total_withdrawn_households_count: number;
    readonly unsuccessful_payments_count: number;
    can_send_to_payment_gateway: boolean;
    readonly can_split: boolean;
    readonly supporting_documents: Array<PaymentPlanSupportingDocument>;
    readonly total_households_count_with_valid_phone_no: number;
    can_create_xlsx_with_fsp_auth_code: boolean;
    fsp_communication_channel: string;
    readonly financial_service_provider: FinancialServiceProvider;
    readonly can_export_xlsx: boolean;
    readonly can_download_xlsx: boolean;
    readonly can_send_xlsx_password: boolean;
    readonly approval_process: Array<ApprovalProcess>;
    /**
     * Total Entitled Quantity USD [sys]
     */
    total_entitled_quantity_usd?: string | null;
    /**
     * Total Entitled Quantity Revised USD [sys]
     */
    total_entitled_quantity_revised_usd?: string | null;
    /**
     * Total Delivered Quantity USD [sys]
     */
    total_delivered_quantity_usd?: string | null;
    /**
     * Total Undelivered Quantity USD [sys]
     */
    total_undelivered_quantity_usd?: string | null;
    /**
     * Male Children Count [sys]
     */
    male_children_count?: number;
    /**
     * Female Children Count [sys]
     */
    female_children_count?: number;
    /**
     * Male Adults Count [sys]
     */
    male_adults_count?: number;
    /**
     * Female Adults Count [sys]
     */
    female_adults_count?: number;
    readonly steficon_rule: Rule;
    readonly source_payment_plan: FollowUpPaymentPlan;
    /**
     * Exchange Rate [sys]
     */
    exchange_rate?: string | null;
    readonly eligible_payments_count: number;
    readonly payment_verification_summary: PaymentVerificationSummary;
    readonly payment_verification_plans: Array<PaymentVerificationPlan>;
    readonly admin_url: string;
};

