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
    /**
     * Program name
     */
    name: string;
    /**
     * Program code
     */
    programme_code?: string | null;
    /**
     * Program status
     *
     * * `ACTIVE` - Active
     * * `DRAFT` - Draft
     * * `FINISHED` - Finished
     */
    status: Status791Enum;
    /**
     * Program start date
     */
    start_date: string;
    /**
     * Program end date
     */
    end_date?: string | null;
    /**
     * Program budget
     */
    budget: string;
    /**
     * Program frequency of payments
     *
     * * `ONE_OFF` - One-off
     * * `REGULAR` - Regular
     */
    frequency_of_payments: FrequencyOfPaymentsEnum;
    /**
     * Program sector
     *
     * * `CHILD_PROTECTION` - Child Protection
     * * `EDUCATION` - Education
     * * `HEALTH` - Health
     * * `MULTI_PURPOSE` - Multi Purpose
     * * `NUTRITION` - Nutrition
     * * `SOCIAL_POLICY` - Social Policy
     * * `WASH` - WASH
     */
    sector: SectorEnum;
    /**
     * Program scope
     *
     * * `FOR_PARTNERS` - For partners
     * * `UNICEF` - Unicef
     */
    scope?: ScopeEnum | null;
    /**
     * Program cash+
     */
    cash_plus: boolean;
    /**
     * Program population goal
     */
    population_goal: number;
    readonly business_area_code: string;
    /**
     * Program beneficiary group
     */
    beneficiary_group: string;
};

