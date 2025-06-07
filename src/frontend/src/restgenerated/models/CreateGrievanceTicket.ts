/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateGrievanceTicketExtras } from './CreateGrievanceTicketExtras';
import type { GrievanceDocumentCreate } from './GrievanceDocumentCreate';
export type CreateGrievanceTicket = {
    description: string;
    assignedTo?: string;
    category: number;
    issueType?: number;
    admin?: string;
    area?: string;
    language: string;
    consent: boolean;
    linkedTickets?: Array<string>;
    extras: CreateGrievanceTicketExtras;
    priority?: number;
    urgency?: number;
    partner?: number;
    program?: string;
    comments?: string;
    linkedFeedbackId?: string;
    documentation?: Array<GrievanceDocumentCreate>;
};

