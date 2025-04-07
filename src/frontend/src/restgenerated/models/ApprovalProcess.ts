/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ApprovalProcess = {
    readonly sentForApprovalBy: string;
    readonly sentForAuthorizationBy: string;
    readonly sentForFinanceReleaseBy: string;
    sentForApprovalDate?: string | null;
    sentForAuthorizationDate?: string | null;
    sentForFinanceReleaseDate?: string | null;
    approvalNumberRequired?: number;
    authorizationNumberRequired?: number;
    financeReleaseNumberRequired?: number;
    readonly rejectedOn: string | null;
    readonly actions: Record<string, any>;
};

