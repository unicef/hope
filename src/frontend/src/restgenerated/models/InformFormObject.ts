/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Minimal representation of an Inform form as returned from the API.
 *
 * Only the ``id`` and ``name`` fields are guaranteed.  The
 * ``dateModified`` field is optional and may be absent depending on the
 * response from the Inform service.
 */
export type InformFormObject = {
    id: string;
    name: string;
    dateModified?: string;
};