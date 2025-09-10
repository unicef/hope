/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaSimple } from './AreaSimple';
import type { DeliveredQuantity } from './DeliveredQuantity';
export type HouseholdSimple = {
    readonly id: string;
    unicefId?: string | null;
    admin1: AreaSimple;
    admin2: AreaSimple;
    admin3: AreaSimple;
    admin4: AreaSimple;
    /**
     * Household first registration date [sys]
     */
    firstRegistrationDate: string;
    /**
     * Household last registration date [sys]
     */
    lastRegistrationDate: string;
    totalCashReceived: string;
    totalCashReceivedUsd: string;
    readonly deliveredQuantities: Array<DeliveredQuantity>;
    /**
     * Data collection start date
     */
    start?: string | null;
    /**
     * Household zip code
     */
    zipCode?: string | null;
    residenceStatus: string;
    countryOrigin?: string;
    country?: string;
    /**
     * Household address
     */
    address?: string;
    /**
     * Household village
     */
    village?: string;
    readonly geopoint: string | null;
    readonly importId: string;
    programSlug: string;
};

