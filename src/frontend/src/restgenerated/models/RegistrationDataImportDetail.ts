/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeduplicationEngineStatusEnum } from './DeduplicationEngineStatusEnum';
export type RegistrationDataImportDetail = {
    readonly id: string;
    name: string;
    status: string;
    statusDisplay: string;
    dataSource: string;
    importedBy?: string;
    readonly createdAt: string;
    /**
     * Abort RDI
     */
    erased?: boolean;
    readonly importDate: string;
    numberOfHouseholds: number;
    numberOfIndividuals: number;
    readonly biometricDeduplicated: string;
    errorMessage?: string;
    readonly canMerge: boolean;
    readonly biometricDeduplicationEnabled: boolean;
    deduplicationEngineStatus?: DeduplicationEngineStatusEnum | null;
    readonly batchDuplicatesCountAndPercentage: Array<Record<string, number>>;
    readonly batchUniqueCountAndPercentage: Array<Record<string, number>>;
    readonly goldenRecordDuplicatesCountAndPercentage: Array<Record<string, number>>;
    readonly goldenRecordPossibleDuplicatesCountAndPercentage: Array<Record<string, number>>;
    readonly goldenRecordUniqueCountAndPercentage: Array<Record<string, number>>;
    readonly totalHouseholdsCountWithValidPhoneNo: number;
    readonly adminUrl: string;
};

