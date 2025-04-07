/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CommunicationChannelEnum } from './CommunicationChannelEnum';
export type FinancialServiceProvider = {
    readonly id: string;
    name: string;
    communicationChannel: CommunicationChannelEnum;
    isPaymentGateway: boolean;
};

