/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CategoryExtras } from './CategoryExtras';
import type { TicketPaymentVerificationDetailsExtras } from './TicketPaymentVerificationDetailsExtras';
import type { UpdateAddIndividualIssueTypeExtras } from './UpdateAddIndividualIssueTypeExtras';
import type { UpdateHouseholdDataUpdateIssueTypeExtras } from './UpdateHouseholdDataUpdateIssueTypeExtras';
import type { UpdateIndividualDataUpdateIssueTypeExtras } from './UpdateIndividualDataUpdateIssueTypeExtras';
export type UpdateGrievanceTicketExtras = {
    householdDataUpdateIssueTypeExtras?: UpdateHouseholdDataUpdateIssueTypeExtras | null;
    individualDataUpdateIssueTypeExtras?: UpdateIndividualDataUpdateIssueTypeExtras | null;
    addIndividualIssueTypeExtras?: UpdateAddIndividualIssueTypeExtras | null;
    category?: CategoryExtras | null;
    ticketPaymentVerificationDetailsExtras?: TicketPaymentVerificationDetailsExtras | null;
};

