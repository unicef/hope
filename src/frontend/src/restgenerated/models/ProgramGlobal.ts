/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { ScopeEnum } from './ScopeEnum';
import type { SectorEnum } from './SectorEnum';
import type { Status791Enum } from './Status791Enum';
export type ProgramGlobal = {
    readonly id: string;
    name: string;
    programme_code?: string | null;
    status: Status791Enum;
    start_date: string;
    end_date?: string | null;
    budget: string;
    frequency_of_payments: FrequencyOfPaymentsEnum;
    sector: SectorEnum;
    scope?: ScopeEnum | null;
    cash_plus: boolean;
    population_goal: number;
    readonly business_area_code: string;
};

