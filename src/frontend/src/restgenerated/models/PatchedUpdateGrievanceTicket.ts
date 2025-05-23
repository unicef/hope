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
    assignedTo?: string;
    admin?: string;
    area?: string;
    language?: string;
    linkedTickets?: Array<string>;
    household?: string;
    individual?: string;
    paymentRecord?: string;
    extras?: UpdateGrievanceTicketExtras;
    priority?: number;
    urgency?: number;
    partner?: number;
    program?: string;
    comments?: string;
    documentation?: Array<CreateGrievanceDocument>;
    documentationToUpdate?: Array<UpdateGrievanceDocument>;
    documentationToDelete?: Array<string>;
};

