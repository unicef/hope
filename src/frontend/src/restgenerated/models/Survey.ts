/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccountabilityFullListArguments } from './AccountabilityFullListArguments';
import type { AccountabilityRandomSamplingArguments } from './AccountabilityRandomSamplingArguments';
export type Survey = {
    readonly id: string;
    unicefId?: string | null;
    title: string;
    body?: string;
    category: string;
    samplingType: string;
    flow?: string;
    flowId?: string | null;
    paymentPlan?: string;
    fullListArguments?: AccountabilityFullListArguments | null;
    randomSamplingArguments?: AccountabilityRandomSamplingArguments | null;
    readonly sampleFilePath: string | null;
    readonly hasValidSampleFile: boolean;
    readonly rapidProUrl: string | null;
    readonly createdAt: string;
    readonly createdBy: string;
};

