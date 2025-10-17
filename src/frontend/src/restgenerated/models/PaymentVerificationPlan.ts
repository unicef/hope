/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentVerificationPlanStatusEnum } from './PaymentVerificationPlanStatusEnum';
export type PaymentVerificationPlan = {
    readonly id: string;
    unicefId?: string | null;
    status?: PaymentVerificationPlanStatusEnum;
    statusDisplay: string;
    verificationChannel: string;
    sampling: string;
    sexFilter?: string | null;
    activationDate?: string | null;
    completionDate?: string | null;
    sampleSize?: number | null;
    respondedCount?: number | null;
    receivedCount?: number | null;
    notReceivedCount?: number | null;
    receivedWithProblemsCount?: number | null;
    confidenceInterval?: number | null;
    marginOfError?: number | null;
    xlsxFileExporting?: boolean;
    xlsxFileImported?: boolean;
    readonly hasXlsxFile: boolean;
    readonly xlsxFileWasDownloaded: boolean;
    error?: string | null;
    readonly ageFilterMin: number | null;
    readonly ageFilterMax: number | null;
    excludedAdminAreasFilter?: any;
    rapidProFlowId?: string;
    readonly adminUrl: string;
};

