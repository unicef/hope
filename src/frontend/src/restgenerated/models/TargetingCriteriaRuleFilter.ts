/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ComparisonMethodEnum } from './ComparisonMethodEnum';
import type { FlexFieldClassificationEnum } from './FlexFieldClassificationEnum';
export type TargetingCriteriaRuleFilter = {
    comparisonMethod: ComparisonMethodEnum;
    flexFieldClassification?: FlexFieldClassificationEnum;
    fieldName: string;
    /**
     *
     * Array of arguments
     *
     */
    arguments: any;
    roundNumber?: number | null;
    readonly fieldAttribute: any;
};

