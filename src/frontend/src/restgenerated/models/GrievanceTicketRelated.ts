/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CategoryD54Enum } from './CategoryD54Enum';
import type { GrievanceTicketStatusEnum } from './GrievanceTicketStatusEnum';
export type GrievanceTicketRelated = {
    readonly id: string;
    unicefId?: string | null;
    category: CategoryD54Enum;
    issueType?: number | null;
    status?: GrievanceTicketStatusEnum;
};

