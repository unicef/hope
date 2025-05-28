/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccountabilityFullListArguments } from './AccountabilityFullListArguments';
import type { AccountabilityRandomSamplingArguments } from './AccountabilityRandomSamplingArguments';
import type { SurveySampleSizeSamplingTypeEnum } from './SurveySampleSizeSamplingTypeEnum';
export type SurveySampleSize = {
    paymentPlan?: string;
    samplingType: SurveySampleSizeSamplingTypeEnum;
    fullListArguments?: AccountabilityFullListArguments;
    randomSamplingArguments: AccountabilityRandomSamplingArguments;
};

