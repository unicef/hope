/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CoreFieldChoice } from './CoreFieldChoice';
import type { FeedbackIssueTypeEnum } from './FeedbackIssueTypeEnum';
export type FieldAttribute = {
    id: string;
    type: FeedbackIssueTypeEnum;
    name: string;
    readonly labels: Array<Record<string, any>>;
    readonly labelEn: string | null;
    hint: string;
    choices: Array<CoreFieldChoice>;
    readonly associatedWith: any;
    readonly isFlexField: boolean;
    readonly pduData: string;
};

