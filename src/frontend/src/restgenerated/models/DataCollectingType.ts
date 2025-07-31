/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataCollectingTypeTypeEnum } from './DataCollectingTypeTypeEnum';
export type DataCollectingType = {
    readonly id: number;
    label: string;
    code: string;
    type?: DataCollectingTypeTypeEnum | null;
    typeDisplay: string;
    individualFiltersAvailable?: boolean;
    householdFiltersAvailable?: boolean;
};

