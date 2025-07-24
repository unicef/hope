/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CountryEnum } from './CountryEnum';
import type { DocumentStatusEnum } from './DocumentStatusEnum';
import type { DocumentTypeEnum } from './DocumentTypeEnum';
import type { RdiMergeStatusEnum } from './RdiMergeStatusEnum';
export type Document = {
    readonly id: string;
    type: DocumentTypeEnum;
    country: CountryEnum;
    image?: string;
    documentNumber: string;
    issuanceDate?: string;
    expiryDate?: string;
    rdiMergeStatus?: RdiMergeStatusEnum;
    isRemoved?: boolean;
    removedDate?: string | null;
    readonly createdAt: string;
    readonly updatedAt: string;
    lastSyncAt?: string | null;
    status?: DocumentStatusEnum;
    cleared?: boolean;
    clearedDate?: string;
    clearedBy?: string | null;
    /**
     * If this object was copied from another, this field will contain the object it was copied from.
     */
    copiedFrom?: string | null;
};

