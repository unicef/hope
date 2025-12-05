/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccountDataField } from './AccountDataField';
export type Account = {
    readonly id: string;
    readonly name: string;
    readonly dataFields: Array<AccountDataField>;
    accountType: number;
    number?: string | null;
    financialInstitution?: number | null;
    accountTypeKey: string;
};

