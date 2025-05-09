/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FeedbackMessage } from './FeedbackMessage';
export type FeedbackList = {
    readonly id: string;
    unicefId?: string | null;
    issueType: string;
    readonly householdUnicefId: string | null;
    readonly householdId: string | null;
    readonly individualUnicefId: string | null;
    readonly individualId: string | null;
    readonly linkedGrievanceId: string | null;
    readonly linkedGrievanceUnicefId: string | null;
    readonly programName: string | null;
    readonly programId: string | null;
    readonly createdBy: string;
    readonly createdAt: string;
    readonly feedbackMessages: Array<FeedbackMessage>;
};

