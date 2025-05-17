/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaList } from './AreaList';
import type { CategoryEnum } from './CategoryEnum';
import type { HouseholdSimple } from './HouseholdSimple';
import type { PriorityEnum } from './PriorityEnum';
import type { StatusEbbEnum } from './StatusEbbEnum';
import type { UrgencyEnum } from './UrgencyEnum';
import type { User } from './User';
export type GrievanceTicketList = {
    readonly id: string;
    unicefId?: string | null;
    status?: StatusEbbEnum;
    readonly programs: Record<string, any>;
    household: HouseholdSimple | null;
    admin?: string;
    admin2: AreaList;
    assignedTo: User;
    createdBy: User;
    /**
     * Date this ticket was most recently changed.
     */
    userModified?: string | null;
    category: CategoryEnum;
    issueType?: number | null;
    priority?: PriorityEnum;
    urgency?: UrgencyEnum;
    readonly createdAt: string;
    readonly updatedAt: string;
    readonly totalDays: number;
    readonly targetId: string;
    readonly relatedTickets: Record<string, any>;
};

