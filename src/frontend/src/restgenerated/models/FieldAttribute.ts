/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CoreFieldChoice } from './CoreFieldChoice';
export type FieldAttribute = {
    id: string;
    type: string;
    name: string;
    readonly labels: Array<Record<string, any>>;
    readonly labelEn: string | null;
    hint: string;
    choices: Array<CoreFieldChoice>;
    readonly associatedWith: any;
    readonly isFlexField: boolean;
    readonly pduData: string;
};

