/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserBusinessArea } from './UserBusinessArea';
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
    businessAreas: Array<UserBusinessArea>;
    readonly permissionsInScope: string;
    readonly userRoles: Record<string, any>;
    readonly partnerRoles: Record<string, any>;
};

