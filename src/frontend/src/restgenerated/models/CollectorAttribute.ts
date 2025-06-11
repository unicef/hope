/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FeedbackIssueTypeEnum } from './FeedbackIssueTypeEnum';
export type CollectorAttribute = {
    id: string;
    type: FeedbackIssueTypeEnum;
    name: string;
    lookup: string;
    label: Record<string, any>;
    hint: string;
    required: boolean;
    choices: Array<string>;
};

