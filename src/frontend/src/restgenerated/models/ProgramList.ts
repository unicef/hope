/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BeneficiaryGroup } from './BeneficiaryGroup';
import type { DataCollectingType } from './DataCollectingType';
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { SectorEnum } from './SectorEnum';
import type { Status791Enum } from './Status791Enum';
export type ProgramList = {
    readonly id: string;
    /**
     * Program code
     */
    programmeCode?: string | null;
    /**
     * Program slug [sys]
     */
    slug: string;
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
    dataCollectingType: DataCollectingType;
    beneficiaryGroup: BeneficiaryGroup;
    /**
     * Status
     *
     * * `ACTIVE` - Active
     * * `DRAFT` - Draft
     * * `FINISHED` - Finished
     */
    status: Status791Enum;
    readonly pduFields: Array<string>;
    /**
     * Program household count [sys]
     */
    householdCount?: number;
    readonly numberOfHouseholdsWithTpInProgram: number;
};

