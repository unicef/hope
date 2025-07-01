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
    startDate: string;
    /**
     * Program end date
     */
    endDate?: string | null;
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
    frequencyOfPayments: FrequencyOfPaymentsEnum;
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
    cashPlus: boolean;
    /**
     * Program population goal
     */
    populationGoal: number;
    /**
     * Program data collecting type
     */
    dataCollectingType: number;
    /**
     * Program beneficiary group
     */
    beneficiaryGroup: string;
};

