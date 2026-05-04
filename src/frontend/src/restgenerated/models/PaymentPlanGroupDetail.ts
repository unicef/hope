/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProgramCycleSmall } from './ProgramCycleSmall';
export type PaymentPlanGroupDetail = {
    readonly id: string;
    unicefId?: string | null;
    name?: string;
    cycle: ProgramCycleSmall;
    readonly createdAt: string;
    readonly totalEntitledQuantityUsd: number;
    readonly totalDeliveredQuantityUsd: number;
    readonly totalUndeliveredQuantityUsd: number;
    readonly paymentPlansCount: number;
};

