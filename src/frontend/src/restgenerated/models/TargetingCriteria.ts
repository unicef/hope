/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TargetingCriteriaRule } from './TargetingCriteriaRule';
export type TargetingCriteria = {
    readonly id: string;
    /**
     * Exclude households with individuals (members or collectors) that have active adjudication ticket(s).
     */
    flag_exclude_if_active_adjudication_ticket?: boolean;
    /**
     * Exclude households with individuals (members or collectors) on sanction list.
     */
    flag_exclude_if_on_sanction_list?: boolean;
    readonly rules: Array<TargetingCriteriaRule>;
};

