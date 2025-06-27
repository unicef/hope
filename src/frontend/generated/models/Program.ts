/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { SectorEnum } from './SectorEnum';
export type Program = {
    readonly id: string;
    name: string;
    start_date: string;
    end_date?: string | null;
    budget: string;
    frequency_of_payments: FrequencyOfPaymentsEnum;
    sector: SectorEnum;
    cash_plus: boolean;
    population_goal: number;
    data_collecting_type: number;
    beneficiary_group: string;
};

