/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FinancialServiceProvider } from './FinancialServiceProvider';
export type DeliveryMechanismPerPaymentPlan = {
    readonly id: string;
    name: string;
    code: string;
    order: string;
    chosen_configuration?: string | null;
    readonly fsp: FinancialServiceProvider;
};

