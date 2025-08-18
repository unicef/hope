/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataTypeEnum } from './DataTypeEnum';
import type { Status753Enum } from './Status753Enum';
export type KoboImportData = {
    readonly id: string;
    readonly status: Status753Enum;
    readonly dataType: DataTypeEnum;
    readonly numberOfHouseholds: number | null;
    readonly numberOfIndividuals: number | null;
    readonly error: string;
    readonly validationErrors: string;
    /**
     * Parse kobo validation errors JSON into structured format.
     */
    readonly koboValidationErrors: Array<Record<string, any>>;
    readonly createdAt: string;
    readonly koboAssetId: string;
    readonly onlyActiveSubmissions: boolean;
    readonly pullPictures: boolean;
    readonly businessAreaSlug: string;
};

