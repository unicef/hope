/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaSimple } from './AreaSimple';
import type { DeliveredQuantity } from './DeliveredQuantity';
import type { ResidenceStatusEnum } from './ResidenceStatusEnum';
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
};

