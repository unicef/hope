/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { Rule } from './Rule';
import type { TargetingCriteria } from './TargetingCriteria';
export type TargetPopulationDetail = {
    id: string;
    unicef_id?: string | null;
    /**
     * Name
     */
    name?: string | null;
    status: string;
    /**
     * Total Households Count [sys]
     */
    total_households_count?: number;
    /**
     * Total Individuals Count [sys]
     */
    total_individuals_count?: number;
    currency: string;
    /**
     * Targeting level exclusion IDs
     */
    excluded_ids?: string | null;
    /**
     * Total Entitled Quantity [sys]
     */
    total_entitled_quantity?: string | null;
    /**
     * Total Delivered Quantity [sys]
     */
    total_delivered_quantity?: string | null;
    /**
     * Total Undelivered Quantity [sys]
     */
    total_undelivered_quantity?: string | null;
    /**
     * Dispersion Start Date
     */
    dispersion_start_date?: string | null;
    /**
     * Dispersion End Date
     */
    dispersion_end_date?: string | null;
    /**
     * Follow Up Payment Plan flag [sys]
     */
    is_follow_up?: boolean;
    readonly follow_ups: Array<FollowUpPaymentPlan>;
    readonly created_by: string;
    readonly created_at: string;
    readonly updated_at: string;
    background_action_status: string;
    /**
     * Payment Plan start date
     */
    start_date?: string | null;
    /**
     * Payment Plan end date
     */
    end_date?: string | null;
    program: string;
    program_cycle: string;
    /**
     * Male Children Count [sys]
     */
    male_children_count?: number;
    /**
     * Female Children Count [sys]
     */
    female_children_count?: number;
    /**
     * Male Adults Count [sys]
     */
    male_adults_count?: number;
    /**
     * Female Adults Count [sys]
     */
    female_adults_count?: number;
    readonly targeting_criteria: TargetingCriteria;
    readonly steficon_rule_targeting: Rule;
};

