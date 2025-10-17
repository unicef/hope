/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SanctionListIndividualDateOfBirth } from './SanctionListIndividualDateOfBirth';
import type { SanctionListIndividualDocument } from './SanctionListIndividualDocument';
export type SanctionListIndividual = {
    readonly id: string;
    fullName: string;
    referenceNumber: string;
    documents: Array<SanctionListIndividualDocument>;
    datesOfBirth: Array<SanctionListIndividualDateOfBirth>;
};

