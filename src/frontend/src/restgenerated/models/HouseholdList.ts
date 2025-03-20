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
    /**
     * Household size
     */
    size?: number | null;
    /**
     * Household residence status
     *
     * * `` - None
     * * `IDP` - Displaced  |  Internally Displaced People
     * * `REFUGEE` - Displaced  |  Refugee / Asylum Seeker
     * * `OTHERS_OF_CONCERN` - Displaced  |  Others of Concern
     * * `HOST` - Non-displaced  |   Host
     * * `NON_HOST` - Non-displaced  |   Non-host
     * * `RETURNEE` - Displaced  |   Returnee
     */
    residence_status?: ResidenceStatusEnum;
    total_cash_received: string;
    total_cash_received_usd: string;
    /**
     * Household last registration date [sys]
     */
    last_registration_date: string;
};

