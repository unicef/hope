/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResidenceStatusEnum } from './ResidenceStatusEnum';
export type HouseholdForTicket = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * Household unhcr id
     */
    unhcrId?: string;
    /**
     * Household village
     */
    village?: string;
    /**
     * Household address
     */
    address?: string;
    admin1?: string;
    admin2?: string;
    country?: string;
    countryOrigin?: string;
    readonly geopoint: string | null;
    headOfHousehold: string;
    /**
     * Household residence status
     *
     * * `` - None
     * * `IDP` - Displaced  |  Internally Displaced People
     * * `REFUGEE` - Displaced  |  Refugee / Asylum Seeker
     * * `OTHERS_OF_CONCERN` - Displaced  |  Others of Concern
     * * `HOST` - Non-displaced  |   Host
     * * `NON_HOST` - Non-displaced  |   Non-host
     * * `RETURNEE` - Displaced  |   Returnee
     */
    residenceStatus?: ResidenceStatusEnum;
    /**
     * Household size
     */
    size?: number | null;
    readonly activeIndividualsCount: number;
};

