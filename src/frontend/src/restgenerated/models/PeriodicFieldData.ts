/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SubtypeEnum } from './SubtypeEnum';
export type PeriodicFieldData = {
    subtype: SubtypeEnum;
    numberOfRounds: number;
    roundsNames?: Array<string>;
    /**
     * Number of rounds already used in templates and cannot be used again in template creation again.
     */
    roundsCovered?: number;
};

