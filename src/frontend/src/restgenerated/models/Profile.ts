/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Partner } from './Partner';
export type Profile = {
    readonly id: string;
    /**
     * Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.
     */
    username: string;
    email: string;
    firstName?: string;
    lastName?: string;
    /**
     * Designates that this user has all permissions without explicitly assigning them.
     */
    isSuperuser?: boolean;
    partner: Partner;
    readonly businessAreas: Record<string, any>;
    readonly permissionsInScope: string;
    readonly userRoles: Record<string, any>;
    readonly partnerRoles: Record<string, any>;
};

