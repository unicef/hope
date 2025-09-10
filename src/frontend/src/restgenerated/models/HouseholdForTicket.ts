/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaSimple } from './AreaSimple';
import type { HeadOfHousehold } from './HeadOfHousehold';
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
    admin1: AreaSimple;
    admin2: AreaSimple;
    country?: string;
    countryOrigin?: string;
    readonly geopoint: string | null;
    headOfHousehold: HeadOfHousehold;
    residenceStatus: string;
    /**
     * Household size
     */
    size?: number | null;
    readonly activeIndividualsCount: number;
    programSlug: string;
};

