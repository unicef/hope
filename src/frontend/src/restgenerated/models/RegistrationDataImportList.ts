/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type RegistrationDataImportList = {
    readonly id: string;
    name: string;
    status: string;
    data_source: string;
    imported_by?: string;
    readonly created_at: string;
    /**
     * Abort RDI
     */
    erased?: boolean;
    readonly import_date: string;
    number_of_households: number;
    number_of_individuals: number;
    readonly biometric_deduplicated: string;
};

