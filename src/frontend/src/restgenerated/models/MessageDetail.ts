/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { HouseholdSmall } from './HouseholdSmall';
import type { MessageDetailSamplingTypeEnum } from './MessageDetailSamplingTypeEnum';
import type { RegistrationDataImportList } from './RegistrationDataImportList';
export type MessageDetail = {
    readonly id: string;
    unicefId?: string | null;
    title: string;
    numberOfRecipients?: number;
    readonly createdBy: string;
    readonly createdAt: string;
    body: string;
    readonly households: Array<HouseholdSmall>;
    readonly paymentPlan: FollowUpPaymentPlan;
    readonly registrationDataImport: RegistrationDataImportList;
    samplingType?: MessageDetailSamplingTypeEnum;
    fullListArguments?: any;
    randomSamplingArguments?: any;
    sampleSize?: number;
    readonly adminUrl: string;
};

