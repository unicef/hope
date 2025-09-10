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
    admin?: string | null;
    area?: string;
    language?: string;
    consent: boolean;
    linkedTickets?: Array<string>;
    extras?: CreateGrievanceTicketExtras | null;
    priority?: number;
    urgency?: number;
    partner?: number | null;
    program?: string | null;
    comments?: string | null;
    linkedFeedbackId?: string | null;
    documentation?: Array<GrievanceDocumentCreate> | null;
};

