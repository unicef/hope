/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuthorizedUser } from './AuthorizedUser';
import type { PDUOnlineEditSentBackComment } from './PDUOnlineEditSentBackComment';
export type PDUOnlineEditDetail = {
    readonly id: number;
    name?: string | null;
    numberOfRecords?: number | null;
    readonly createdAt: string;
    createdBy?: string;
    status: string;
    statusDisplay: string;
    readonly isAuthorized: boolean;
    approvedBy?: string;
    approvedAt?: string | null;
    sentBackComment: PDUOnlineEditSentBackComment;
    editData?: any;
    authorizedUsers: Array<AuthorizedUser>;
    readonly isCreator: boolean;
    readonly adminUrl: string;
};
