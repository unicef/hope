/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PartnerAccessEnum } from './PartnerAccessEnum';
import type { PartnersData } from './PartnersData';
export type ProgramUpdatePartnerAccess = {
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
};

