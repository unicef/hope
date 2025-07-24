/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaSimple } from './AreaSimple';
import type { FeedbackMessage } from './FeedbackMessage';
import type { IssueTypeEnum } from './IssueTypeEnum';
export type FeedbackDetail = {
    readonly id: string;
    unicefId?: string | null;
    issueType: IssueTypeEnum;
    householdUnicefId: string | null;
    householdId: string | null;
    individualUnicefId: string | null;
    individualId: string | null;
    readonly linkedGrievanceId: string | null;
    linkedGrievanceUnicefId: string | null;
    linkedGrievanceCategory: string | null;
    programName: string | null;
    readonly programId: string | null;
    readonly createdBy: string;
    readonly createdAt: string;
    readonly feedbackMessages: Array<FeedbackMessage>;
    readonly adminUrl: string;
    description: string;
    area?: string;
    language?: string;
    comments?: string | null;
    consent?: boolean;
    readonly updatedAt: string;
    admin2: AreaSimple;
};

