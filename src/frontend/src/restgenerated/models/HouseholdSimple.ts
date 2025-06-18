/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaSimple } from './AreaSimple';
import type { DeliveredQuantity } from './DeliveredQuantity';
export type HouseholdSimple = {
    readonly id: string;
    unicefId?: string | null;
    admin2: AreaSimple;
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
};

