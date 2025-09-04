/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CountryEnum } from './CountryEnum';
import type { DocumentSerializerUploadStatusEnum } from './DocumentSerializerUploadStatusEnum';
import type { RdiMergeStatusEnum } from './RdiMergeStatusEnum';
import type { Type69cEnum } from './Type69cEnum';
export type DocumentSerializerUpload = {
    readonly id: string;
    type: Type69cEnum;
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
    status?: DocumentSerializerUploadStatusEnum;
    cleared?: boolean;
    clearedDate?: string;
    clearedBy?: string | null;
    /**
     * If this object was copied from another, this field will contain the object it was copied from.
     */
    copiedFrom?: string | null;
};

