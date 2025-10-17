/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TransferTypeEnum } from './TransferTypeEnum';
export type DeliveryMechanism = {
    readonly id: string;
    name: string;
    code: string;
    isActive?: boolean;
    transferType?: TransferTypeEnum;
    accountType?: number | null;
};

