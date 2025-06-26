/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateGrievanceDocument } from './CreateGrievanceDocument';
import type { UpdateGrievanceDocument } from './UpdateGrievanceDocument';
import type { UpdateGrievanceTicketExtras } from './UpdateGrievanceTicketExtras';
export type PatchedUpdateGrievanceTicket = {
    version?: number;
    description?: string;
    assignedTo?: string | null;
    admin?: string | null;
    area?: string;
    language?: string;
    linkedTickets?: Array<string>;
    household?: string;
    individual?: string;
    paymentRecord?: string;
    extras?: UpdateGrievanceTicketExtras;
    priority?: number;
    urgency?: number;
    partner?: number | null;
    program?: string | null;
    comments?: string | null;
    documentation?: Array<CreateGrievanceDocument> | null;
    documentationToUpdate?: Array<UpdateGrievanceDocument> | null;
    documentationToDelete?: Array<string>;
};

