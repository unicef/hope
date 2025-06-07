/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type DeduplicationResult = {
    readonly unicefId: string;
    hitId?: string;
    fullName?: string;
    score?: number;
    proximityToScore?: number;
    readonly location: string;
    readonly age: number | null;
    readonly duplicate: boolean;
    readonly distinct: boolean;
};

