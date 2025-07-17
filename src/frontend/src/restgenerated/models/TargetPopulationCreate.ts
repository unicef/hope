/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TargetingCriteriaRule } from './TargetingCriteriaRule';
export type TargetPopulationCreate = {
    readonly id: string;
    readonly version: number;
    name: string;
    programCycleId: string;
    rules: TargetingCriteriaRule;
    excludedIds?: string;
    exclusionReason?: string;
    fspId?: string | null;
    deliveryMechanismCode?: string | null;
    vulnerabilityScoreMin?: string;
    vulnerabilityScoreMax?: string;
};

