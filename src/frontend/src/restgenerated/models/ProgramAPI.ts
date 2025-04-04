/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { SectorEnum } from './SectorEnum';
export type ProgramAPI = {
    readonly id: string;
    /**
     * Program name
     */
    name: string;
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
     * Program cash+
     */
    cash_plus: boolean;
    /**
     * Program population goal
     */
    population_goal: number;
    /**
     * Program data collecting type
     */
    data_collecting_type: number;
    /**
     * Program beneficiary group
     */
    beneficiary_group: string;
};

