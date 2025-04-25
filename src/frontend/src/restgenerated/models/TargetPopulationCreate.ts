/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TargetingCriteria } from './TargetingCriteria';
export type TargetPopulationCreate = {
    readonly id: string;
    readonly version: number;
    name: string;
    programCycleId: string;
    targetingCriteria: TargetingCriteria;
    excludedIds?: string;
    exclusionReason?: string;
    fspId?: string;
    deliveryMechanismCode?: string;
    vulnerabilityScoreMin?: string;
    vulnerabilityScoreMax?: string;
};

