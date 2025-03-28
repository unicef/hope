/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Approval } from './Approval';
export type ApprovalProcess = {
    readonly approvals: Array<Approval>;
    readonly sent_for_approval_by: string;
    readonly sent_for_authorization_by: string;
    readonly sent_for_finance_release_by: string;
    sent_for_approval_date?: string | null;
    sent_for_authorization_date?: string | null;
    sent_for_finance_release_date?: string | null;
    approval_number_required?: number;
    authorization_number_required?: number;
    finance_release_number_required?: number;
    readonly created_at: string;
};

