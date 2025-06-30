/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HeadOfHousehold } from './HeadOfHousehold';
export type Recipient = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * Household size
     */
    size?: number | null;
    headOfHousehold: HeadOfHousehold;
};

