/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PriorityEnum } from './PriorityEnum';
import type { UrgencyEnum } from './UrgencyEnum';
export type BeneficiaryTicketCreate = {
    description: string;
    program?: string | null;
    priority?: PriorityEnum;
    urgency?: UrgencyEnum;
    assignedTo?: string | null;
};

