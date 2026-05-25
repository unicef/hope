/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PaymentVerificationPlanList = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * The currency code following the ISO 4217 standard (e.g. USD, EUR)
     */
    readonly currency: string | null;
    /**
     * Total Delivered Quantity [sys]
     */
    totalDeliveredQuantity?: string | null;
    programCycleStartDate: string;
    programCycleEndDate: string;
    verificationStatus: string;
    /**
     * Dispersion Start Date
     */
    dispersionStartDate?: string | null;
    /**
     * Dispersion End Date
     */
    dispersionEndDate?: string | null;
    readonly updatedAt: string;
    programCycleTitle: string;
};

