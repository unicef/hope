/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AreaSimple } from './AreaSimple';
import type { ConsentSharingEnum } from './ConsentSharingEnum';
import type { HeadOfHousehold } from './HeadOfHousehold';
import type { OrgEnumeratorEnum } from './OrgEnumeratorEnum';
import type { RegistrationDataImport } from './RegistrationDataImport';
import type { RegistrationMethodEnum } from './RegistrationMethodEnum';
export type HouseholdDetail = {
    readonly id: string;
    unicefId?: string | null;
    headOfHousehold: HeadOfHousehold;
    admin1: AreaSimple;
    admin2: AreaSimple;
    admin3: AreaSimple;
    admin4: AreaSimple;
    program: string;
    country?: string;
    countryOrigin?: string;
    readonly status: string;
    totalCashReceived: string;
    totalCashReceivedUsd: string;
    readonly sanctionListPossibleMatch: boolean;
    readonly sanctionListConfirmedMatch: boolean;
    readonly hasDuplicates: boolean;
    registrationDataImport: RegistrationDataImport;
    readonly flexFields: Record<string, any>;
    readonly linkedGrievances: Record<string, any>;
    readonly adminAreaTitle: string;
    readonly activeIndividualsCount: number;
    readonly geopoint: string | null;
    readonly importId: string | null;
    readonly adminUrl: string | null;
    /**
     * Household male children count
     */
    maleChildrenCount?: number | null;
    /**
     * Household female children count
     */
    femaleChildrenCount?: number | null;
    /**
     * Household children disabled count
     */
    childrenDisabledCount?: number | null;
    readonly currency: string | null;
    /**
     * Household first registration date [sys]
     */
    firstRegistrationDate: string;
    /**
     * Household last registration date [sys]
     */
    lastRegistrationDate: string;
    /**
     * Household unhcr id
     */
    unhcrId?: string;
    /**
     * Household village
     */
    village?: string;
    /**
     * Household address
     */
    address?: string;
    /**
     * Household zip code
     */
    zipCode?: string | null;
    /**
     * Household female age group 0-5
     */
    femaleAgeGroup05Count?: number | null;
    /**
     * Household female age group 6-11
     */
    femaleAgeGroup611Count?: number | null;
    /**
     * Household female age group 12-17
     */
    femaleAgeGroup1217Count?: number | null;
    /**
     * Household female age group 18-59
     */
    femaleAgeGroup1859Count?: number | null;
    /**
     * Household female age group 60
     */
    femaleAgeGroup60Count?: number | null;
    /**
     * Household pregnant count
     */
    pregnantCount?: number | null;
    /**
     * Household male age group 0-5
     */
    maleAgeGroup05Count?: number | null;
    /**
     * Household male age group 6-11
     */
    maleAgeGroup611Count?: number | null;
    /**
     * Household male age group 12-17
     */
    maleAgeGroup1217Count?: number | null;
    /**
     * Household male age group 18-59
     */
    maleAgeGroup1859Count?: number | null;
    /**
     * Household male age group 60
     */
    maleAgeGroup60Count?: number | null;
    /**
     * Household female age group 0-5
     */
    femaleAgeGroup05DisabledCount?: number | null;
    /**
     * Household female age group 6-11
     */
    femaleAgeGroup611DisabledCount?: number | null;
    /**
     * Household female age group 12-17
     */
    femaleAgeGroup1217DisabledCount?: number | null;
    /**
     * Household female age group 18-59
     */
    femaleAgeGroup1859DisabledCount?: number | null;
    /**
     * Household female age group 60
     */
    femaleAgeGroup60DisabledCount?: number | null;
    /**
     * Household male age group 0-5
     */
    maleAgeGroup05DisabledCount?: number | null;
    /**
     * Household male age group 6-1
     */
    maleAgeGroup611DisabledCount?: number | null;
    /**
     * Household male age group 12-17
     */
    maleAgeGroup1217DisabledCount?: number | null;
    /**
     * Household male age group 18-59
     */
    maleAgeGroup1859DisabledCount?: number | null;
    /**
     * Household male age group 60
     */
    maleAgeGroup60DisabledCount?: number | null;
    /**
     * Household other sex group count
     */
    otherSexGroupCount?: number | null;
    /**
     * Data collection start date
     */
    start?: string | null;
    /**
     * Household deviceid [sys]
     */
    deviceid?: string;
    /**
     * Female child headed household flag
     */
    fchildHoh?: boolean | null;
    /**
     * Child headed household flag
     */
    childHoh?: boolean | null;
    /**
     * Household returnee status
     */
    returnee?: boolean | null;
    /**
     * Household size
     */
    size?: number | null;
    residenceStatus: string;
    /**
     * Beneficiary Program Registration id [sys]
     */
    programRegistrationId?: string | null;
    readonly deliveredQuantities: Record<string, any>;
    readonly facilityName: string;
    /**
     * Household consent
     */
    consent?: boolean | null;
    /**
     * Household name enumerator [sys]
     */
    nameEnumerator?: string;
    /**
     * Household org enumerator [sys]
     *
     * * `` - None
     * * `PARTNER` - Partner
     * * `UNICEF` - UNICEF
     */
    orgEnumerator?: OrgEnumeratorEnum;
    /**
     * Household org name enumerator [sys]
     */
    orgNameEnumerator?: string;
    /**
     * Household registration method [sys]
     *
     * * `` - None
     * * `COMMUNITY` - Community-level Registration
     * * `HH_REGISTRATION` - Household Registration
     */
    registrationMethod?: RegistrationMethodEnum;
    /**
     * Household consent sharing
     *
     * * `` - None
     * * `GOVERNMENT_PARTNER` - Government partners
     * * `HUMANITARIAN_PARTNER` - Humanitarian partners
     * * `PRIVATE_PARTNER` - Private partners
     * * `UNICEF` - UNICEF
     */
    consentSharing?: ConsentSharingEnum;
    readonly rolesInHousehold: Record<string, any>;
};

