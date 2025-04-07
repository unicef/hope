/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataSourceEnum } from './DataSourceEnum';
import type { RegistrationDataImportStatusEnum } from './RegistrationDataImportStatusEnum';
import type { User } from './User';
export type RegistrationDataImport = {
    id: string;
    name: string;
    status?: RegistrationDataImportStatusEnum;
    readonly importDate: string;
    numberOfIndividuals: number;
    numberOfHouseholds: number;
    importedBy: User;
    dataSource: DataSourceEnum;
};

