/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
export type PaymentPlan = {
    id: string;
    unicef_id?: string | null;
    name?: string | null;
    status: string;
    target_population?: string | null;
    total_households_count?: number;
    currency: string;
    total_entitled_quantity?: string | null;
    total_delivered_quantity?: string | null;
    total_undelivered_quantity?: string | null;
    dispersion_start_date?: string | null;
    dispersion_end_date?: string | null;
    is_follow_up?: boolean;
    readonly follow_ups: Array<FollowUpPaymentPlan>;
    program: string;
    program_id: string;
    readonly last_approval_process_date: string | null;
    readonly last_approval_process_by: string | null;
};

