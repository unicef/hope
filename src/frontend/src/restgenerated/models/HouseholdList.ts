/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaSimple } from './AreaSimple';
export type HouseholdList = {
    readonly id: string;
    unicefId?: string | null;
    headOfHousehold: string;
    admin1: AreaSimple;
    admin2: AreaSimple;
    readonly status: string;
    /**
     * Household size
     */
    size?: number | null;
    residenceStatus: string;
    totalCashReceived: string;
    totalCashReceivedUsd: string;
    /**
     * Household last registration date [sys]
     */
    lastRegistrationDate: string;
    /**
     * Household first registration date [sys]
     */
    firstRegistrationDate: string;
    readonly currency: string | null;
    hasDuplicates: boolean;
    sanctionListPossibleMatch: boolean;
    sanctionListConfirmedMatch: boolean;
    /**
     * Household program
     */
    readonly programId: string;
    programName: string;
    programCode: string;
    readonly facilityName: string;
};

