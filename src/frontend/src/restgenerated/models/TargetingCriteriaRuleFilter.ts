/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ComparisonMethod7bbEnum } from './ComparisonMethod7bbEnum';
import type { FlexFieldClassificationEnum } from './FlexFieldClassificationEnum';
export type TargetingCriteriaRuleFilter = {
    comparisonMethod: ComparisonMethod7bbEnum;
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

