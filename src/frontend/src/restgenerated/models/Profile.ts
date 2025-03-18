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
    first_name?: string;
    last_name?: string;
    /**
     * Designates that this user has all permissions without explicitly assigning them.
     */
    is_superuser?: boolean;
    business_areas: Array<UserBusinessArea>;
    readonly permissions_in_scope: string;
    readonly user_roles: Record<string, any>;
    readonly partner_roles: Record<string, any>;
};

