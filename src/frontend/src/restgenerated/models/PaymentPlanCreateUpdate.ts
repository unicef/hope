/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PaymentPlanCreateUpdate = {
    readonly id: string;
    targetPopulationId: string;
    dispersionStartDate: string;
    dispersionEndDate: string;
    /**
     * The currency code following the ISO 4217 standard (e.g. USD, EUR)
     */
    currency: string | null;
    readonly version: number;
};

