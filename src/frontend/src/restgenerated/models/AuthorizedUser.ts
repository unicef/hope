/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AuthorizedUser = {
    readonly id: string;
    firstName?: string;
    lastName?: string;
    /**
     * Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.
     */
    username: string;
    email: string;
    readonly pduPermissions: Array<string>;
};

