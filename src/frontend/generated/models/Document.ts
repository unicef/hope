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
    document_number: string;
    rdi_merge_status?: RdiMergeStatusEnum;
    is_removed?: boolean;
    is_original?: boolean;
    readonly created_at: string;
    readonly updated_at: string;
    last_sync_at?: string | null;
    status?: DocumentStatusEnum;
    cleared?: boolean;
    cleared_date?: string;
    issuance_date?: string | null;
    expiry_date?: string | null;
    is_migration_handled?: boolean;
    cleared_by?: string | null;
    /**
     * If this object was copied from another, this field will contain the object it was copied from.
     */
    copied_from?: string | null;
};

