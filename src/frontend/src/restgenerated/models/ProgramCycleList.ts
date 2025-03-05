/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ProgramCycleList = {
    readonly id: string;
    title?: string | null;
    status: string;
    start_date: string;
    end_date: string;
    program_start_date: string;
    program_end_date: string;
    readonly created_at: string;
    readonly total_entitled_quantity_usd: number;
    readonly total_undelivered_quantity_usd: number;
    readonly total_delivered_quantity_usd: number;
    readonly frequency_of_payments: string;
    readonly created_by: string;
    readonly admin_url: string | null;
    readonly can_remove_cycle: boolean;
};

