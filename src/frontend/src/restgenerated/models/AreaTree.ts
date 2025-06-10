/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaChildrenTree } from './AreaChildrenTree';
export type AreaTree = {
    readonly id: string;
    name: string;
    pCode?: string | null;
    readonly areas: Array<AreaChildrenTree>;
    readonly level: number;
};

