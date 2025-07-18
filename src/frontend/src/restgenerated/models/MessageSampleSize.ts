/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccountabilityFullListArguments } from './AccountabilityFullListArguments';
import type { AccountabilityRandomSamplingArguments } from './AccountabilityRandomSamplingArguments';
import type { SamplingTypeE86Enum } from './SamplingTypeE86Enum';
export type MessageSampleSize = {
    households?: Array<string>;
    paymentPlan?: string | null;
    registrationDataImport?: string | null;
    samplingType: SamplingTypeE86Enum;
    fullListArguments?: AccountabilityFullListArguments | null;
    randomSamplingArguments?: AccountabilityRandomSamplingArguments | null;
};

