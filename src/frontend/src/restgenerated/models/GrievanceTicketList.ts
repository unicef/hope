/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CategoryD54Enum } from './CategoryD54Enum';
import type { GrievanceTicketStatusEnum } from './GrievanceTicketStatusEnum';
import type { PriorityEnum } from './PriorityEnum';
import type { UrgencyEnum } from './UrgencyEnum';
import type { User } from './User';
export type GrievanceTicketList = {
    readonly id: string;
    admin?: string;
    unicefId?: string | null;
    status?: GrievanceTicketStatusEnum;
    householdUnicefId?: string;
    individualUnicefId?: string;
    individualId?: string;
    householdId?: string;
    assignedTo: User;
    /**
     * Date this ticket was most recently changed.
     */
    userModified?: string | null;
    category: CategoryD54Enum;
    issueType?: number | null;
    priority?: PriorityEnum;
    urgency?: UrgencyEnum;
    readonly createdAt: string;
    createdBy: User;
    readonly totalDays: number | null;
    readonly relatedTickets: Record<string, any>;
    readonly programs: Record<string, any>;
    readonly targetId: string;
};

