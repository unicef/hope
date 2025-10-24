/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaSimple } from './AreaSimple';
import type { HeadOfHousehold } from './HeadOfHousehold';
export type Recipient = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * Household size
     */
    size?: number | null;
    headOfHousehold: HeadOfHousehold;
    admin2: AreaSimple;
    readonly status: string;
    residenceStatus: string;
    /**
     * Household last registration date [sys]
     */
    lastRegistrationDate: string;
};

