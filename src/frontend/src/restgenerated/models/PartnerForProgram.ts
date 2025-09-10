/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializer for Partner model.
 *
 * It expects Partner objects to be annotated with partner_program which is the program that is serializing the object
 */
export type PartnerForProgram = {
    readonly id: number;
    name: string;
    readonly areaAccess: string;
    readonly areas: Record<string, any>;
};

