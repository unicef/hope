/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
export type PaymentPlan = {
    id: string;
    unicef_id?: string | null;
    /**
     * Name
     */
    name?: string | null;
    status: string;
    /**
     * Target Criteria
     */
    targeting_criteria: string;
    /**
     * Total Households Count [sys]
     */
    total_households_count?: number;
    currency: string;
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
    program: string;
    program_id: string;
    program_cycle_id: string;
    readonly last_approval_process_date: string | null;
    readonly last_approval_process_by: string | null;
    readonly admin_url: string;
};

