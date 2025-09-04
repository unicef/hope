/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RdiMergeStatusEnum } from './RdiMergeStatusEnum';
export type AccountSerializerUpload = {
    readonly id: string;
    accountType: string;
    number?: string;
    financialInstitution?: number;
    data?: any;
    rdiMergeStatus?: RdiMergeStatusEnum;
    readonly createdAt: string;
    readonly updatedAt: string;
    active?: boolean;
};

