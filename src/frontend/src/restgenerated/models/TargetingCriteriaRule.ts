/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TargetingCollectorRuleFilterBlock } from './TargetingCollectorRuleFilterBlock';
import type { TargetingCriteriaRuleFilter } from './TargetingCriteriaRuleFilter';
import type { TargetingIndividualRuleFilterBlock } from './TargetingIndividualRuleFilterBlock';
export type TargetingCriteriaRule = {
    readonly id: string;
    household_ids?: string;
    individual_ids?: string;
    readonly filters: Array<TargetingCriteriaRuleFilter>;
    readonly individuals_filters_blocks: Array<TargetingIndividualRuleFilterBlock>;
    readonly collectors_filters_blocks: Array<TargetingCollectorRuleFilterBlock>;
};

