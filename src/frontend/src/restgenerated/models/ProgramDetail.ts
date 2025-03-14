/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BeneficiaryGroup } from './BeneficiaryGroup';
import type { DataCollectingType } from './DataCollectingType';
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { PartnerAccessEnum } from './PartnerAccessEnum';
import type { SectorEnum } from './SectorEnum';
import type { Status791Enum } from './Status791Enum';
export type ProgramDetail = {
    id: string;
    programme_code?: string | null;
    slug: string;
    name: string;
    start_date: string;
    end_date?: string | null;
    budget: string;
    frequency_of_payments: FrequencyOfPaymentsEnum;
    sector: SectorEnum;
    cash_plus: boolean;
    population_goal: number;
    data_collecting_type: DataCollectingType;
    beneficiary_group: BeneficiaryGroup;
    /**
     * Status
     *
     * * `ACTIVE` - Active
     * * `DRAFT` - Draft
     * * `FINISHED` - Finished
     */
    status: Status791Enum;
    readonly pdu_fields: Array<string>;
    household_count?: number;
    readonly just_in_case: string;
    readonly admin_url: string;
    description?: string;
    administrative_areas_of_implementation?: string;
    /**
     * record revision number
     */
    version?: number;
    readonly partners: Record<string, any>;
    partner_access?: PartnerAccessEnum;
    readonly registration_imports_total_count: number;
    readonly target_populations_count: number;
};

