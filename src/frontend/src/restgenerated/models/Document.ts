/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Country } from './Country';
import type { DocumentType } from './DocumentType';
export type Document = {
    readonly id: string;
    type: DocumentType;
    country: Country;
    documentNumber?: string;
    photo?: string;
};

