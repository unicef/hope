/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FullList } from './FullList';
import type { RandomSampling } from './RandomSampling';
import type { SamplingTypeE86Enum } from './SamplingTypeE86Enum';
export type MessageCreate = {
    title: string;
    body: string;
    samplingType: SamplingTypeE86Enum;
    fullListArguments?: FullList | null;
    randomSamplingArguments?: RandomSampling | null;
    paymentPlan?: string | null;
    registrationDataImport?: string | null;
    households?: Array<string>;
};

