/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PaymentVerificationPlan = {
    readonly id: string;
    status: string;
    verification_channel: string;
    sampling: string;
    sex_filter?: string | null;
    activation_date?: string | null;
    completion_date?: string | null;
    sample_size?: number | null;
    responded_count?: number | null;
    received_count?: number | null;
    not_received_count?: number | null;
    received_with_problems_count?: number | null;
    confidence_interval?: number | null;
    margin_of_error?: number | null;
    xlsx_file_exporting?: boolean;
    xlsx_file_imported?: boolean;
    error?: string | null;
};

