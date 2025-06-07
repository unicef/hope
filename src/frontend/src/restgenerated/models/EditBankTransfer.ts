/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FeedbackIssueTypeEnum } from './FeedbackIssueTypeEnum';
export type EditBankTransfer = {
    id: string;
    type: FeedbackIssueTypeEnum;
    bankName: string;
    bankAccountNumber: string;
    bankBranchName?: string;
    accountHolderName: string;
};

