/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PaymentVerificationPlan = {
    readonly id: string;
    status: string;
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
    error?: string | null;
};

