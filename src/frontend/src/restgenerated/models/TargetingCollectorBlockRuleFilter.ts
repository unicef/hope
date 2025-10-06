/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FlexFieldClassificationEnum } from './FlexFieldClassificationEnum';
import type { TargetingCollectorBlockRuleFilterComparisonMethodEnum } from './TargetingCollectorBlockRuleFilterComparisonMethodEnum';
export type TargetingCollectorBlockRuleFilter = {
    comparisonMethod: TargetingCollectorBlockRuleFilterComparisonMethodEnum;
    flexFieldClassification?: FlexFieldClassificationEnum;
    fieldName: string;
    /**
     *
     * Array of arguments
     *
     */
    arguments: any;
};

