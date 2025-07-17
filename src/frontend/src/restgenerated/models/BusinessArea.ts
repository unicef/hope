/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type BusinessArea = {
    readonly id: string;
    name: string;
    code: string;
    longName: string;
    slug: string;
    parent?: string | null;
    isSplit?: boolean;
    active?: boolean;
    /**
     * Enable screen beneficiary against sanction list
     */
    screenBeneficiary?: boolean;
    isAccountabilityApplicable?: boolean;
};

