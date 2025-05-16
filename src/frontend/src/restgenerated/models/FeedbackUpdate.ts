/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { IssueTypeEnum } from './IssueTypeEnum';
export type FeedbackUpdate = {
    issueType: IssueTypeEnum;
    householdLookup?: string | null;
    individualLookup?: string | null;
    area?: string | null;
    admin2?: string | null;
    description: string;
    language?: string;
    comments?: string | null;
    consent?: boolean;
};

