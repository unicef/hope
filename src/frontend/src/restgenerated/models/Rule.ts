/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RuleTypeEnum } from './RuleTypeEnum';
export type Rule = {
    readonly id: number;
    name: string;
    description?: string | null;
    /**
     * Use Rule for Targeting or Payment Plan
     *
     * * `PAYMENT_PLAN` - Payment Plan
     * * `TARGETING` - Targeting
     */
    type?: RuleTypeEnum;
};

