/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type RegistrationDataImportList = {
    readonly id: string;
    name: string;
    status: string;
    dataSource: string;
    importedBy?: string;
    readonly createdAt: string;
    /**
     * Abort RDI
     */
    erased?: boolean;
    readonly importDate: string;
    numberOfHouseholds: number;
    numberOfIndividuals: number;
    readonly biometricDeduplicated: string;
};

