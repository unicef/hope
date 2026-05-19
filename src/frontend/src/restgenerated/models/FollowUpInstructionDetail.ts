/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FollowUpInstructionChildPaymentPlanSummary } from './FollowUpInstructionChildPaymentPlanSummary';
export type FollowUpInstructionDetail = {
    readonly id: string;
    unicefId?: string | null;
    readonly status: string;
    readonly backgroundActionStatus: string;
    backgroundActionStatusDisplay: string;
    readonly childPaymentPlansCount: number;
    readonly householdsCount: number;
    readonly totalEntitledQuantity: number;
    readonly totalDeliveredQuantity: number;
    readonly totalUndeliveredQuantity: number;
    readonly exportFileLink: string;
    readonly hasExportFile: boolean;
    readonly createdAt: string;
    readonly updatedAt: string;
    readonly adminUrl: string | null;
    readonly paymentPlans: Array<FollowUpInstructionChildPaymentPlanSummary>;
};

