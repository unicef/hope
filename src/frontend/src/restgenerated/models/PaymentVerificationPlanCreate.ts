/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FullList } from './FullList';
import type { RandomSampling } from './RandomSampling';
import type { RapidPro } from './RapidPro';
export type PaymentVerificationPlanCreate = {
    sampling: string;
    verificationChannel: string;
    fullListArguments: FullList | null;
    randomSamplingArguments: RandomSampling | null;
    rapidProArguments: RapidPro | null;
};

