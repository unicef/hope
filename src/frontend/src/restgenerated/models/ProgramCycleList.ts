/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ProgramCycleList = {
    readonly id: string;
    title?: string | null;
    status: string;
    startDate: string;
    endDate: string;
    programStartDate: string;
    programEndDate: string;
    readonly createdAt: string;
    readonly totalEntitledQuantityUsd: number;
    readonly totalUndeliveredQuantityUsd: number;
    readonly totalDeliveredQuantityUsd: number;
    readonly frequencyOfPayments: string;
    readonly createdBy: string;
    readonly adminUrl: string | null;
    readonly canRemoveCycle: boolean;
};

