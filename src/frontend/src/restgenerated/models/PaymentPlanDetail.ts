/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Choice } from './Choice';
import type { DeliveryMechanismPerPaymentPlan } from './DeliveryMechanismPerPaymentPlan';
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { HouseholdDetail } from './HouseholdDetail';
import type { PaymentPlanSupportingDocument } from './PaymentPlanSupportingDocument';
import type { ReconciliationSummary } from './ReconciliationSummary';
import type { VolumeByDeliveryMechanism } from './VolumeByDeliveryMechanism';
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
    excluded_ids?: string;
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
    background_action_status: string;
    /**
     * Payment Plan start date
     */
    start_date?: string | null;
    /**
     * Payment Plan end date
     */
    end_date?: string | null;
    program: string;
    has_payment_list_export_file: boolean;
    readonly has_fsp_delivery_mechanism_xlsx_template: boolean;
    imported_file_name: string;
    readonly payments_conflicts_count: number;
    readonly delivery_mechanisms: Array<DeliveryMechanismPerPaymentPlan>;
    readonly volume_by_delivery_mechanism: Array<VolumeByDeliveryMechanism>;
    readonly split_choices: Array<Choice>;
    bank_reconciliation_success: number;
    bank_reconciliation_error: number;
    can_create_payment_verification_plan: boolean;
    readonly available_payment_records_count: number;
    readonly reconciliation_summary: ReconciliationSummary;
    readonly excluded_households: Array<HouseholdDetail>;
    readonly can_create_follow_up: boolean;
    readonly total_withdrawn_households_count: number;
    readonly unsuccessful_payments_count: number;
    can_send_to_payment_gateway: boolean;
    readonly can_split: boolean;
    readonly supporting_documents: Array<PaymentPlanSupportingDocument>;
    readonly total_households_count_with_valid_phone_no: number;
    can_create_xlsx_with_fsp_auth_code: boolean;
    fsp_communication_channel: string;
    readonly can_export_xlsx: boolean;
    readonly can_download_xlsx: boolean;
    readonly can_send_xlsx_password: boolean;
};

