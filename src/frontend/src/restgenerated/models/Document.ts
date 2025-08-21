/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CountryEnum } from './CountryEnum';
import type { DocumentTypeEnum } from './DocumentTypeEnum';
export type Document = {
    type: DocumentTypeEnum;
    country: CountryEnum;
    image?: string;
    documentNumber: string;
    issuanceDate?: string;
    expiryDate?: string;
};

