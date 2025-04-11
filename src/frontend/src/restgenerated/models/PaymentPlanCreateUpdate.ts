/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CurrencyEnum } from './CurrencyEnum';
export type PaymentPlanCreateUpdate = {
    readonly id: string;
    targetPopulationId: string;
    dispersionStartDate: string;
    dispersionEndDate: string;
    currency: CurrencyEnum;
    readonly version: number;
};

