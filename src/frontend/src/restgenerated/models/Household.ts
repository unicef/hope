/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectTypeEnum } from './CollectTypeEnum';
import type { ConsentSharingEnum } from './ConsentSharingEnum';
import type { CountryEnum } from './CountryEnum';
import type { CountryOriginEnum } from './CountryOriginEnum';
import type { OrgEnumeratorEnum } from './OrgEnumeratorEnum';
import type { RdiMergeStatusEnum } from './RdiMergeStatusEnum';
import type { RegistrationMethodEnum } from './RegistrationMethodEnum';
import type { ResidenceStatusEnum } from './ResidenceStatusEnum';
export type Household = {
    firstRegistrationDate?: string;
    lastRegistrationDate?: string;
    country?: CountryEnum | null;
    countryOrigin?: CountryOriginEnum | null;
    consentSharing?: Array<ConsentSharingEnum>;
    village?: string | null;
    consentSign?: string;
    headOfHouseholdId: string | null;
    primaryCollectorId: string | null;
    alternateCollectorId?: string | null;
    members: Array<string>;
    admin1?: string | null;
    admin2?: string | null;
    admin3?: string | null;
    admin4?: string | null;
    /**
     * Facility/Organization name
     */
    facilityName?: string | null;
    /**
     * Facility/Organization p_code (is required when facility_name provided)
     */
    facilityAdminArea?: string | null;
    rdiMergeStatus?: RdiMergeStatusEnum;
    isRemoved?: boolean;
    removedDate?: string | null;
    readonly createdAt: string;
    readonly updatedAt: string;
    lastSyncAt?: string | null;
    internalData?: any;
    /**
     * Household consent
     */
    consent?: boolean | null;
    /**
     * Household residence status
     *
     * * `` - None
     * * `IDP` - Displaced  |  Internally Displaced People
     * * `IDP_RETURNEE` - Displaced  |  Internally Displaced People Returnee
     * * `REFUGEE` - Displaced  |  Refugee / Asylum Seeker
     * * `OTHERS_OF_CONCERN` - Displaced  |  Others of Concern
     * * `HOST` - Non-displaced  |   Host
     * * `NON_HOST` - Non-displaced  |   Non-host
     * * `RETURNEE` - Displaced  |   Refugee Returnee
     */
    residenceStatus?: ResidenceStatusEnum;
    /**
     * Household address
     */
    address?: string;
    /**
     * Household zip code
     */
    zipCode?: string | null;
    /**
     * Household size
     */
    size?: number | null;
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
     * Household children count
     */
    childrenCount?: number | null;
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
    /**
     * Household male children disabled count
     */
    maleChildrenDisabledCount?: number | null;
    /**
     * Household female children disabled count
     */
    femaleChildrenDisabledCount?: number | null;
    /**
     * Household other sex group count
     */
    otherSexGroupCount?: number | null;
    /**
     * Household unknown sex group count
     */
    unknownSexGroupCount?: number | null;
    /**
     * Household returnee status
     */
    returnee?: boolean | null;
    /**
     * Female child headed household flag
     */
    fchildHoh?: boolean | null;
    /**
     * Child headed household flag
     */
    childHoh?: boolean | null;
    /**
     * Household currency (legacy, pending removal)
     */
    currencyOld?: string;
    /**
     * Household unhcr id
     */
    unhcrId?: string;
    /**
     * A unified external reference with a fixed-length source prefix (XLS, KOB, or AUR)
     * and a source-specific identifier separated by '#', e.g., 'KOB#321#123'.
     */
    originatingId?: string | null;
    /**
     * Data collection start date
     */
    start?: string | null;
    /**
     * Household registration method [sys]
     *
     * * `` - None
     * * `COMMUNITY` - Community-level Registration
     * * `HH_REGISTRATION` - Household Registration
     */
    registrationMethod?: RegistrationMethodEnum;
    /**
     * Family ID eDopomoga household id [sys]
     */
    familyId?: string | null;
    /**
     * Household origin unicef id [sys]
     */
    originUnicefId?: string | null;
    /**
     * Household migration status [sys]
     */
    isMigrationHandled?: boolean;
    /**
     * Household migrated at [sys]
     */
    migratedAt?: string | null;
    /**
     * Household collect type [sys]
     *
     * * `STANDARD` - Standard
     * * `SINGLE` - Single
     */
    collectType?: CollectTypeEnum;
    /**
     * Beneficiary Program Registration id [sys]
     */
    programRegistrationId?: string | null;
    /**
     * Household cash received usd [sys]
     */
    totalCashReceivedUsd?: string | null;
    /**
     * Household cash received [sys]
     */
    totalCashReceived?: string | null;
    /**
     * Household flex fields [sys]
     */
    flexFields?: any;
    /**
     * Household withdrawn [sys]
     */
    withdrawn?: boolean;
    /**
     * Household withdrawn date [sys]
     */
    withdrawnDate?: string | null;
    /**
     * Household deviceid [sys]
     */
    deviceid?: string;
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
     * Household enumerator record [sys]
     */
    enumeratorRecId?: number | null;
    /**
     * Household flex registrations record [sys]
     */
    flexRegistrationsRecordId?: number | null;
    /**
     * Key used to identify Collisions in the system
     */
    identificationKey?: string | null;
    /**
     * Collection of household representations
     */
    householdCollection?: number | null;
    /**
     * Household storage object
     */
    storageObj?: number | null;
    /**
     * If this household was copied from another household, this field will contain the household it was copied from.
     */
    copiedFrom?: string | null;
    facility?: string | null;
    /**
     * Household currency
     */
    currency?: number | null;
    /**
     * This is only used to track collector (primary or secondary) of a household.
     * They may still be a HOH of this household or any other household.
     * Through model will contain the role (ROLE_CHOICE) they are connected with on.
     */
    readonly representatives: Array<string>;
    /**
     * This relation is filed when collision of Household happens.
     */
    extraRdis?: Array<string>;
};

