/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccountabilityFullListArguments } from './AccountabilityFullListArguments';
import type { AccountabilityRandomSamplingArguments } from './AccountabilityRandomSamplingArguments';
import type { SurveySampleSizeSamplingTypeEnum } from './SurveySampleSizeSamplingTypeEnum';
export type SurveySampleSize = {
    paymentPlan?: string | null;
    samplingType: SurveySampleSizeSamplingTypeEnum | null;
    fullListArguments?: AccountabilityFullListArguments | null;
    randomSamplingArguments?: AccountabilityRandomSamplingArguments | null;
};

