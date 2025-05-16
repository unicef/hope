/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TargetingCollectorRuleFilterBlock } from './TargetingCollectorRuleFilterBlock';
import type { TargetingCriteriaRuleFilter } from './TargetingCriteriaRuleFilter';
import type { TargetingIndividualRuleFilterBlock } from './TargetingIndividualRuleFilterBlock';
export type TargetingCriteriaRule = {
    householdIds?: string;
    individualIds?: string;
    householdsFiltersBlocks?: Array<TargetingCriteriaRuleFilter>;
    individualsFiltersBlocks?: Array<TargetingIndividualRuleFilterBlock>;
    collectorsFiltersBlocks?: Array<TargetingCollectorRuleFilterBlock>;
};

