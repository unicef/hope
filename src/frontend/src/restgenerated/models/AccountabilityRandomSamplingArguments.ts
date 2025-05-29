/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccountabilityCommunicationMessageAgeInput } from './AccountabilityCommunicationMessageAgeInput';
export type AccountabilityRandomSamplingArguments = {
    excludedAdminAreas: Array<string>;
    confidenceInterval: number;
    marginOfError: number;
    age?: AccountabilityCommunicationMessageAgeInput;
    sex?: string;
};

