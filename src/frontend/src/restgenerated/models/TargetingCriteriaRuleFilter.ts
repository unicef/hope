/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ComparisonMethod7bbEnum } from './ComparisonMethod7bbEnum';
import type { FlexFieldClassificationEnum } from './FlexFieldClassificationEnum';
export type TargetingCriteriaRuleFilter = {
    readonly id: string;
    comparison_method: ComparisonMethod7bbEnum;
    flex_field_classification?: FlexFieldClassificationEnum;
    field_name: string;
    /**
     *
     * Array of arguments
     *
     */
    arguments: any;
    round_number?: number | null;
};

