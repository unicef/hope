/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Status791Enum } from './Status791Enum';
export type ProgramSmall = {
    readonly id: string;
    /**
     * Program code
     */
    programmeCode?: string | null;
    /**
     * Program slug [sys]
     */
    slug: string;
    /**
     * Program name
     */
    name: string;
    /**
     * Program status
     *
     * * `ACTIVE` - Active
     * * `DRAFT` - Draft
     * * `FINISHED` - Finished
     */
    status: Status791Enum;
    readonly screenBeneficiary: boolean;
};

