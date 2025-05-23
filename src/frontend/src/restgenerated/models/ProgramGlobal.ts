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
    programmeCode?: string | null;
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
     * Program scope
     *
     * * `FOR_PARTNERS` - For partners
     * * `UNICEF` - Unicef
     */
    scope?: ScopeEnum | null;
    /**
     * Program cash+
     */
    cashPlus: boolean;
    /**
     * Program population goal
     */
    populationGoal: number;
    readonly businessAreaCode: string;
    /**
     * Program beneficiary group
     */
    beneficiaryGroup: string;
};

