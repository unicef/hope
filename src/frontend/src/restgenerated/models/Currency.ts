/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type Currency = {
    readonly id: number;
    /**
     * The currency code following the ISO 4217 standard (e.g. USD, EUR)
     */
    code: string;
    /**
     * The full name of the currency
     */
    name: string;
    /**
     * Whether this is a cryptocurrency (e.g. USDC)
     */
    isCrypto?: boolean;
};

