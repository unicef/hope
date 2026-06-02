/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentPlanStatusEnum } from './PaymentPlanStatusEnum';
export type FollowUpInstructionChildPaymentPlanSummary = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * Name
     */
    name?: string | null;
    /**
     * Status [sys]
     *
     * * `TP_OPEN` - Open
     * * `TP_LOCKED` - Locked
     * * `PROCESSING` - Processing
     * * `STEFICON_WAIT` - Steficon Wait
     * * `STEFICON_RUN` - Steficon Run
     * * `STEFICON_COMPLETED` - Steficon Completed
     * * `STEFICON_ERROR` - Steficon Error
     * * `DRAFT` - Draft
     * * `PREPARING` - Preparing
     * * `OPEN` - Open
     * * `LOCKED` - Locked
     * * `LOCKED_FSP` - Locked FSP
     * * `IN_APPROVAL` - In Approval
     * * `IN_AUTHORIZATION` - In Authorization
     * * `IN_REVIEW` - In Review
     * * `ACCEPTED` - Accepted
     * * `ABORTED` - Aborted
     * * `FINISHED` - Finished
     * * `CLOSED` - Closed
     */
    status?: PaymentPlanStatusEnum;
    /**
     * The currency code following the ISO 4217 standard (e.g. USD, EUR)
     */
    readonly currency: string | null;
    readonly sourcePaymentPlanId: string;
    readonly sourcePaymentPlanUnicefId: string;
    readonly sourcePaymentPlanName: string;
    readonly householdsCount: number;
    readonly totalEntitledQuantity: number;
    readonly totalEntitledQuantityUsd: number;
    readonly totalDeliveredQuantity: number;
    readonly totalDeliveredQuantityUsd: number;
    readonly totalUndeliveredQuantity: number;
    readonly totalUndeliveredQuantityUsd: number;
};

