/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccountabilityFullListArguments } from './AccountabilityFullListArguments';
import type { AccountabilityRandomSamplingArguments } from './AccountabilityRandomSamplingArguments';
import type { SurveyCategoryEnum } from './SurveyCategoryEnum';
export type Survey = {
    readonly id: string;
    unicefId?: string | null;
    title: string;
    body?: string;
    category: SurveyCategoryEnum;
    samplingType: string;
    flow?: string;
    flowId?: string | null;
    paymentPlan?: string | null;
    fullListArguments?: AccountabilityFullListArguments | null;
    randomSamplingArguments?: AccountabilityRandomSamplingArguments | null;
    readonly sampleFilePath: string | null;
    readonly hasValidSampleFile: boolean;
    readonly rapidProUrl: string | null;
    numberOfRecipients?: number;
    readonly createdAt: string;
    readonly createdBy: string;
};

