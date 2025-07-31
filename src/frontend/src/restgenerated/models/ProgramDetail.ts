/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BeneficiaryGroup } from './BeneficiaryGroup';
import type { DataCollectingType } from './DataCollectingType';
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { PartnerAccessEnum } from './PartnerAccessEnum';
import type { PeriodicField } from './PeriodicField';
import type { ProgramStatusEnum } from './ProgramStatusEnum';
import type { SectorEnum } from './SectorEnum';
export type ProgramDetail = {
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
    status: ProgramStatusEnum;
    pduFields: Array<PeriodicField>;
    /**
     * Program household count [sys]
     */
    householdCount?: number;
    readonly numberOfHouseholdsWithTpInProgram: number;
    readonly adminUrl: string;
    /**
     * Program description
     */
    description?: string;
    /**
     * Program administrative area of implementation
     */
    administrativeAreasOfImplementation?: string;
    /**
     * record revision number
     */
    version?: number;
    readonly partners: Record<string, any>;
    /**
     * Program partner access
     *
     * * `ALL_PARTNERS_ACCESS` - All partners access
     * * `NONE_PARTNERS_ACCESS` - None partners access
     * * `SELECTED_PARTNERS_ACCESS` - Selected partners access
     */
    partnerAccess?: PartnerAccessEnum;
    readonly registrationImportsTotalCount: number;
    readonly targetPopulationsCount: number;
    readonly screenBeneficiary: boolean;
};

