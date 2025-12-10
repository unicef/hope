/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataTypeEnum } from './DataTypeEnum';
import type { StatusF63Enum } from './StatusF63Enum';
export type ImportData = {
    readonly id: string;
    readonly status: StatusF63Enum;
    readonly dataType: DataTypeEnum;
    readonly numberOfHouseholds: number | null;
    readonly numberOfIndividuals: number | null;
    readonly error: string;
    readonly validationErrors: string;
    /**
     * Parse validation errors JSON into structured format.
     */
    readonly xlsxValidationErrors: Array<Record<string, any>>;
    readonly createdAt: string;
    readonly businessAreaSlug: string;
};

