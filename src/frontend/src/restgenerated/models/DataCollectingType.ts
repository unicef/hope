/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FeedbackIssueTypeEnum } from './FeedbackIssueTypeEnum';
export type DataCollectingType = {
    readonly id: number;
    label: string;
    code: string;
    type: FeedbackIssueTypeEnum;
    householdFiltersAvailable?: boolean;
    individualFiltersAvailable?: boolean;
};

