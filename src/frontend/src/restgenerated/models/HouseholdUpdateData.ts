/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HouseholdUpdateRoles } from './HouseholdUpdateRoles';
export type HouseholdUpdateData = {
    adminAreaTitle?: string;
    status?: string;
    consent?: boolean | null;
    consentSharing?: Array<string>;
    residenceStatus?: string;
    countryOrigin?: string;
    country?: string;
    size?: number;
    address?: string;
    femaleAgeGroup05Count?: number;
    femaleAgeGroup611Count?: number;
    femaleAgeGroup1217Count?: number;
    femaleAgeGroup1859Count?: number;
    femaleAgeGroup60Count?: number;
    pregnantCount?: number;
    maleAgeGroup05Count?: number;
    maleAgeGroup611Count?: number;
    maleAgeGroup1217Count?: number;
    maleAgeGroup1859Count?: number;
    maleAgeGroup60Count?: number;
    femaleAgeGroup05DisabledCount?: number;
    femaleAgeGroup611DisabledCount?: number;
    femaleAgeGroup1217DisabledCount?: number;
    femaleAgeGroup1859DisabledCount?: number;
    femaleAgeGroup60DisabledCount?: number;
    maleAgeGroup05DisabledCount?: number;
    maleAgeGroup611DisabledCount?: number;
    maleAgeGroup1217DisabledCount?: number;
    maleAgeGroup1859DisabledCount?: number;
    maleAgeGroup60DisabledCount?: number;
    returnee?: boolean | null;
    fchildHoh?: boolean;
    childHoh?: boolean;
    start?: string;
    nameEnumerator?: string;
    orgEnumerator?: string;
    orgNameEnumerator?: string;
    village?: string;
    registrationMethod?: string;
    currency?: string;
    unhcrId?: string;
    flexFields?: any;
    roles?: Array<HouseholdUpdateRoles>;
};

