/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeduplicationEngineStatusEnum } from './DeduplicationEngineStatusEnum';
export type RegistrationDataImportDetail = {
    readonly id: string;
    name: string;
    status: string;
    data_source: string;
    imported_by?: string;
    readonly created_at: string;
    /**
     * Abort RDI
     */
    erased?: boolean;
    readonly import_date: string;
    number_of_households: number;
    number_of_individuals: number;
    readonly biometric_deduplicated: string;
    error_message?: string;
    readonly can_merge: boolean;
    readonly biometric_deduplication_enabled: boolean;
    deduplication_engine_status?: DeduplicationEngineStatusEnum | null;
    readonly batch_duplicates_count_and_percentage: Array<Record<string, number>>;
    readonly batch_unique_count_and_percentage: Array<Record<string, number>>;
    readonly golden_record_duplicates_count_and_percentage: Array<Record<string, number>>;
    readonly golden_record_possible_duplicates_count_and_percentage: Array<Record<string, number>>;
    readonly golden_record_unique_count_and_percentage: Array<Record<string, number>>;
};

