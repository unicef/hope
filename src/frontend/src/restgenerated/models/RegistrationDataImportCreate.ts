/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type RegistrationDataImportCreate = {
    importFromProgramId: string;
    /**
     * String of Ind or HH ids separated by comma
     */
    importFromIds: string;
    name: string;
    screenBeneficiary: boolean;
    excludeExternalCollectors?: boolean;
};

