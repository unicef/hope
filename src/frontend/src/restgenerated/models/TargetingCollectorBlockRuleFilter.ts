/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FlexFieldClassificationEnum } from './FlexFieldClassificationEnum';
import type { TargetingCollectorBlockRuleFilterComparisonMethodEnum } from './TargetingCollectorBlockRuleFilterComparisonMethodEnum';
export type TargetingCollectorBlockRuleFilter = {
    readonly id: string;
    comparison_method: TargetingCollectorBlockRuleFilterComparisonMethodEnum;
    flex_field_classification?: FlexFieldClassificationEnum;
    field_name: string;
    /**
     *
     * Array of arguments
     *
     */
    arguments: any;
};

