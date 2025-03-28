/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApprovalTypeEnum } from './ApprovalTypeEnum';
export type Approval = {
    type?: ApprovalTypeEnum;
    comment?: string | null;
    readonly created_by: string;
    readonly info: string;
    readonly created_at: string;
};

