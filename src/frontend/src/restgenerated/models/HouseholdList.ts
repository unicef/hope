/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResidenceStatusEnum } from './ResidenceStatusEnum';
export type HouseholdList = {
    id: string;
    unicef_id: string | null;
    head_of_household: string;
    admin1?: string;
    admin2?: string;
    program: string;
    readonly status: string;
    size?: number | null;
    residence_status?: ResidenceStatusEnum;
    total_cash_received: string;
    total_cash_received_usd: string;
    last_registration_date: string;
};

