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
    readonly import_date: string;
    number_of_individuals: number;
    number_of_households: number;
    imported_by: User;
    data_source: DataSourceEnum;
};

