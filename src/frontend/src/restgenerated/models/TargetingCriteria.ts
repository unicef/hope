/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TargetingCriteriaRule } from './TargetingCriteriaRule';
export type TargetingCriteria = {
    /**
     * Exclude households with individuals (members or collectors) that have active adjudication ticket(s).
     */
    flagExcludeIfActiveAdjudicationTicket?: boolean;
    /**
     * Exclude households with individuals (members or collectors) on sanction list.
     */
    flagExcludeIfOnSanctionList?: boolean;
    rules: Array<TargetingCriteriaRule>;
};

