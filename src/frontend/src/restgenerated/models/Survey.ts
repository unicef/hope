/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccountabilityFullListArguments } from './AccountabilityFullListArguments';
import type { AccountabilityRandomSamplingArguments } from './AccountabilityRandomSamplingArguments';
export type Survey = {
    readonly id: string;
    title: string;
    body?: string;
    category: string;
    samplingType: string;
    flow: string;
    paymentPlan: string;
    fullListArguments: AccountabilityFullListArguments;
    randomSamplingArguments: AccountabilityRandomSamplingArguments;
    readonly sampleFilePath: string | null;
    readonly hasValidSampleFile: boolean;
    readonly rapidProUrl: string | null;
};

