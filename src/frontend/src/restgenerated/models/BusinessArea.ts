/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CountrySmall } from './CountrySmall';
export type BusinessArea = {
    readonly id: string;
    name: string;
    code: string;
    longName: string;
    slug: string;
    parent?: string | null;
    isSplit?: boolean;
    active?: boolean;
    isAccountabilityApplicable?: boolean;
    readonly countries: Array<CountrySmall>;
};

