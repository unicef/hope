/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { User } from './User';
export type TicketNote = {
    readonly id: string;
    /**
     * The content of the customers query.
     */
    description: string;
    createdBy: User;
    readonly createdAt: string;
    readonly updatedAt: string;
};

