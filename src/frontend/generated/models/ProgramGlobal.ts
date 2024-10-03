/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BlankEnum } from './BlankEnum';
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { NullEnum } from './NullEnum';
import type { ProgramGlobalStatusEnum } from './ProgramGlobalStatusEnum';
import type { ScopeEnum } from './ScopeEnum';
import type { SectorEnum } from './SectorEnum';
export type ProgramGlobal = {
    readonly id: string;
    name: string;
    programme_code?: string | null;
    status: ProgramGlobalStatusEnum;
    start_date: string;
    end_date?: string | null;
    budget: string;
    frequency_of_payments: FrequencyOfPaymentsEnum;
    sector: SectorEnum;
    scope?: (ScopeEnum | BlankEnum | NullEnum) | null;
    cash_plus: boolean;
    population_goal: number;
    readonly business_area_code: string;
};

