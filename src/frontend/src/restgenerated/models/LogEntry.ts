/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContentType } from './ContentType';
export type LogEntry = {
    objectId?: string | null;
    action: string;
    changes?: any;
    readonly timestamp: string;
    readonly isUserGenerated: boolean | null;
    contentType: ContentType;
    objectRepr?: string;
    readonly user: string;
};

