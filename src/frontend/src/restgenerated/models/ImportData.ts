/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataTypeEnum } from './DataTypeEnum';
import type { Status753Enum } from './Status753Enum';
export type ImportData = {
    readonly id: string;
    readonly status: Status753Enum;
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

