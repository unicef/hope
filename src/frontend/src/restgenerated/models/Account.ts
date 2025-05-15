/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RdiMergeStatusEnum } from './RdiMergeStatusEnum';
export type Account = {
    readonly id: string;
    accountType: string;
    number?: string;
    financialInstitution?: string;
    data?: any;
    rdiMergeStatus?: RdiMergeStatusEnum;
    readonly createdAt: string;
    readonly updatedAt: string;
    active?: boolean;
};

