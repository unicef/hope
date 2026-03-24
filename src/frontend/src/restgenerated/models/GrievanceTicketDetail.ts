/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaList } from './AreaList';
import type { CategoryD54Enum } from './CategoryD54Enum';
import type { GrievanceTicketStatusEnum } from './GrievanceTicketStatusEnum';
import type { HouseholdForTicket } from './HouseholdForTicket';
import type { IndividualSimple } from './IndividualSimple';
import type { Partner } from './Partner';
import type { PriorityEnum } from './PriorityEnum';
import type { TicketNote } from './TicketNote';
import type { UrgencyEnum } from './UrgencyEnum';
import type { User } from './User';
export type GrievanceTicketDetail = {
    readonly id: string;
    unicefId?: string | null;
    status?: GrievanceTicketStatusEnum;
    readonly programs: Record<string, any>;
    household: HouseholdForTicket | null;
    individual: IndividualSimple | null;
    admin?: string;
    admin2: AreaList;
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
    readonly updatedAt: string;
    readonly totalDays: number | null;
    readonly targetId: string;
    readonly relatedTickets: Record<string, any>;
    readonly adminUrl: string | null;
    consent?: boolean;
    partner: Partner;
    postponeDeduplication: boolean;
    /**
     * The content of the customers query.
     */
    description?: string;
    language?: string;
    area?: string;
    readonly paymentRecord: Record<string, any> | null;
    readonly linkedTickets: Record<string, any>;
    readonly existingTickets: Record<string, any>;
    comments?: string | null;
    readonly documentation: Record<string, any>;
    ticketNotes: Array<TicketNote>;
    readonly ticketDetails: Record<string, any> | null;
};

