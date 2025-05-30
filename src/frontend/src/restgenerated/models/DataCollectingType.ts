/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataCollectingTypeEnum } from './DataCollectingTypeEnum';
export type DataCollectingType = {
  readonly id: number;
  label: string;
  code: string;
  type: DataCollectingTypeEnum;
  householdFiltersAvailable?: boolean;
  individualFiltersAvailable?: boolean;
};
