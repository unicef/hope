/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaList } from './AreaList';
import type { CategoryD86Enum } from './CategoryD86Enum';
import type { GrievanceTicketStatusEnum } from './GrievanceTicketStatusEnum';
import type { HouseholdSimple } from './HouseholdSimple';
import type { IndividualSmall } from './IndividualSmall';
import type { PriorityEnum } from './PriorityEnum';
import type { UrgencyEnum } from './UrgencyEnum';
import type { User } from './User';
export type GrievanceTicketList = {
    readonly id: string;
    unicefId?: string | null;
    status?: GrievanceTicketStatusEnum;
    readonly programs: Record<string, any>;
    household: HouseholdSimple | null;
    individual: IndividualSmall | null;
    admin?: string;
    admin2: AreaList;
    assignedTo: User;
    createdBy: User;
    /**
     * Date this ticket was most recently changed.
     */
    userModified?: string | null;
    category: CategoryD86Enum;
    issueType?: number | null;
    priority?: PriorityEnum;
    urgency?: UrgencyEnum;
    readonly createdAt: string;
    readonly updatedAt: string;
    readonly totalDays: number | null;
    readonly targetId: string;
    readonly relatedTickets: Record<string, any>;
};

