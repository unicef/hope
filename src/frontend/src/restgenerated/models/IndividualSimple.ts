/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HouseholdSimple } from './HouseholdSimple';
export type IndividualSimple = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * Full Name of the Beneficiary
     */
    fullName: string;
    household: HouseholdSimple;
    readonly rolesInHouseholds: Record<string, any>;
};

