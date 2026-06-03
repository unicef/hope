/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentPlanBackgroundActionStatusEnum } from './PaymentPlanBackgroundActionStatusEnum';
import type { PaymentPlanGroupBatch } from './PaymentPlanGroupBatch';
import type { ProgramCycleSmall } from './ProgramCycleSmall';
export type PaymentPlanGroupDetail = {
    readonly id: string;
    unicefId?: string | null;
    name?: string;
    cycle: ProgramCycleSmall;
    readonly createdAt: string;
    backgroundActionStatus?: PaymentPlanBackgroundActionStatusEnum | null;
    readonly totalEntitledQuantityUsd: number;
    readonly totalDeliveredQuantityUsd: number;
    readonly totalUndeliveredQuantityUsd: number;
    readonly paymentPlansCount: number;
    readonly canSendToPaymentGateway: boolean;
    readonly batches: Array<PaymentPlanGroupBatch>;
    readonly deliveryImportFile: string | null;
};

