/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { PDUFieldsUpdate } from './PDUFieldsUpdate';
import type { SectorEnum } from './SectorEnum';
export type ProgramUpdate = {
    programmeCode?: string | null;
    /**
     * Program name
     */
    name: string;
    readonly slug: string;
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
     * Program description
     */
    description?: string;
    /**
     * Program budget
     */
    budget: string;
    /**
     * Program administrative area of implementation
     */
    administrativeAreasOfImplementation?: string;
    /**
     * Program population goal
     */
    populationGoal: number;
    /**
     * Program cash+
     */
    cashPlus: boolean;
    /**
     * Program frequency of payments
     *
     * * `ONE_OFF` - One-off
     * * `REGULAR` - Regular
     */
    frequencyOfPayments: FrequencyOfPaymentsEnum;
    dataCollectingType: string;
    /**
     * Program beneficiary group
     */
    beneficiaryGroup: string;
    startDate: string;
    endDate: string | null;
    pduFields: Array<PDUFieldsUpdate>;
    version?: number;
    readonly status: string;
    readonly partnerAccess: string;
};

