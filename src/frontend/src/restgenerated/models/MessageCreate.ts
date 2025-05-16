/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FullList } from './FullList';
import type { MessageCreateSamplingTypeEnum } from './MessageCreateSamplingTypeEnum';
import type { RandomSampling } from './RandomSampling';
export type MessageCreate = {
    title: string;
    body: string;
    samplingType: MessageCreateSamplingTypeEnum;
    fullListArguments: FullList;
    randomSamplingArguments: RandomSampling | null;
    paymentPlan?: string;
    registrationDataImport?: string;
    households?: Array<string>;
};

