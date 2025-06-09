/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { PartnerAccessEnum } from './PartnerAccessEnum';
import type { PartnersData } from './PartnersData';
import type { PDUFieldsCreate } from './PDUFieldsCreate';
import type { SectorEnum } from './SectorEnum';
export type ProgramCreate = {
    readonly id: string;
    programmeCode: string | null;
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
    pduFields: Array<PDUFieldsCreate>;
    partners: Array<PartnersData>;
    /**
     * Program partner access
     *
     * * `ALL_PARTNERS_ACCESS` - All partners access
     * * `NONE_PARTNERS_ACCESS` - None partners access
     * * `SELECTED_PARTNERS_ACCESS` - Selected partners access
     */
    partnerAccess?: PartnerAccessEnum;
    readonly version: number;
    readonly status: string;
};

