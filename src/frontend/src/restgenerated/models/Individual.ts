/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Account } from './Account';
import type { BiometricDeduplicationBatchStatusEnum } from './BiometricDeduplicationBatchStatusEnum';
import type { BiometricDeduplicationGoldenRecordStatusEnum } from './BiometricDeduplicationGoldenRecordStatusEnum';
import type { CommsDisabilityEnum } from './CommsDisabilityEnum';
import type { DeduplicationGoldenRecordStatusEnum } from './DeduplicationGoldenRecordStatusEnum';
import type { DisabilityEnum } from './DisabilityEnum';
import type { Document } from './Document';
import type { HearingDisabilityEnum } from './HearingDisabilityEnum';
import type { MemoryDisabilityEnum } from './MemoryDisabilityEnum';
import type { PhysicalDisabilityEnum } from './PhysicalDisabilityEnum';
import type { PreferredLanguageEnum } from './PreferredLanguageEnum';
import type { RdiMergeStatusEnum } from './RdiMergeStatusEnum';
import type { RelationshipEnum } from './RelationshipEnum';
import type { SeeingDisabilityEnum } from './SeeingDisabilityEnum';
import type { SelfcareDisabilityEnum } from './SelfcareDisabilityEnum';
import type { SexEnum } from './SexEnum';
import type { WorkStatusEnum } from './WorkStatusEnum';
export type Individual = {
    firstRegistrationDate?: string;
    lastRegistrationDate?: string;
    readonly household: string;
    role?: string;
    observedDisability?: string;
    countryOrigin?: string;
    maritalStatus?: string;
    documents?: Array<Document>;
    birthDate: string;
    accounts?: Array<Account>;
    photo?: string;
    rdiMergeStatus?: RdiMergeStatusEnum;
    isRemoved?: boolean;
    removedDate?: string | null;
    lastSyncAt?: string | null;
    internalData?: any;
    /**
     * Individual ID
     */
    individualId?: string;
    /**
     * Full Name of the Beneficiary
     */
    fullName: string;
    /**
     * First name of the Beneficiary
     */
    givenName?: string;
    /**
     * Middle name of the Beneficiary
     */
    middleName?: string;
    /**
     * Last name of the Beneficiary
     */
    familyName?: string;
    /**
     * Beneficiary gender
     *
     * * `MALE` - Male
     * * `FEMALE` - Female
     * * `OTHER` - Other
     * * `NOT_COLLECTED` - Not collected
     * * `NOT_ANSWERED` - Not answered
     */
    sex: SexEnum;
    /**
     * Estimated birth date flag
     */
    estimatedBirthDate?: boolean;
    /**
     * Beneficiary phone number
     */
    phoneNo?: string;
    /**
     * Beneficiary phone number alternative
     */
    phoneNoAlternative?: string;
    /**
     * Beneficiary email address
     */
    email?: string;
    /**
     * Beneficiary contact phone number
     */
    paymentDeliveryPhoneNo?: string | null;
    /**
     * This represents the MEMBER relationship. can be blank
     * as well if household is null!
     *
     * * `UNKNOWN` - Unknown
     * * `AUNT_UNCLE` - Aunt / Uncle
     * * `BROTHER_SISTER` - Brother / Sister
     * * `COUSIN` - Cousin
     * * `DAUGHTERINLAW_SONINLAW` - Daughter-in-law / Son-in-law
     * * `GRANDDAUGHER_GRANDSON` - Granddaughter / Grandson
     * * `GRANDMOTHER_GRANDFATHER` - Grandmother / Grandfather
     * * `HEAD` - Head of household (self)
     * * `MOTHER_FATHER` - Mother / Father
     * * `MOTHERINLAW_FATHERINLAW` - Mother-in-law / Father-in-law
     * * `NEPHEW_NIECE` - Nephew / Niece
     * * `NON_BENEFICIARY` - Not a Family Member. Can only act as a recipient.
     * * `OTHER` - Other
     * * `SISTERINLAW_BROTHERINLAW` - Sister-in-law / Brother-in-law
     * * `SON_DAUGHTER` - Son / Daughter
     * * `WIFE_HUSBAND` - Wife / Husband
     * * `FOSTER_CHILD` - Foster child
     * * `FREE_UNION` - Free union
     */
    relationship?: RelationshipEnum;
    /**
     * Work status
     *
     * * `1` - Yes
     * * `0` - No
     * * `NOT_PROVIDED` - Not provided
     */
    workStatus?: WorkStatusEnum;
    /**
     * Pregnant status
     */
    pregnant?: boolean | null;
    /**
     * Child is female and Head of Household flag
     */
    fchildHoh?: boolean;
    /**
     * Child is Head of Household flag
     */
    childHoh?: boolean;
    /**
     * Disability status
     *
     * * `disabled` - disabled
     * * `not disabled` - not disabled
     */
    disability?: DisabilityEnum;
    /**
     * Disability certificate picture
     */
    disabilityCertificatePicture?: string | null;
    /**
     * Seeing disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    seeingDisability?: SeeingDisabilityEnum;
    /**
     * Hearing disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    hearingDisability?: HearingDisabilityEnum;
    /**
     * Physical disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    physicalDisability?: PhysicalDisabilityEnum;
    /**
     * Memory disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    memoryDisability?: MemoryDisabilityEnum;
    /**
     * Selfcare disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    selfcareDisability?: SelfcareDisabilityEnum;
    /**
     * Comms disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    commsDisability?: CommsDisabilityEnum;
    /**
     * Who answers phone number
     */
    whoAnswersPhone?: string;
    /**
     * Who answers alternative phone number
     */
    whoAnswersAltPhone?: string;
    /**
     * Preferred language
     *
     * * `en-us` - English | English
     * * `ar-ae` -  | عربيArabic
     * * `cs-cz` - čeština | Czech
     * * `de-de` - Deutsch
     * * `es-es` - Español | Spanish
     * * `fr-fr` - Français | French
     * * `hu-hu` - Magyar | Hungarian
     * * `it-it` - Italiano
     * * `pl-pl` - Polskie | Polish
     * * `pt-pt` - Português
     * * `ro-ro` - Română
     * * `ru-ru` - Русский | Russian
     * * `si-si` - සිංහල | Sinhala
     * * `ta-ta` - தமிழ் | Tamil
     * * `uk-ua` - український | Ukrainian
     * * `hi-hi` - हिंदी
     */
    preferredLanguage?: PreferredLanguageEnum | null;
    /**
     * Relationship confirmed status
     */
    relationshipConfirmed?: boolean;
    /**
     * Cryptocurrency wallet name
     */
    walletName?: string;
    /**
     * Cryptocurrency blockchain name
     */
    blockchainName?: string;
    /**
     * Cryptocurrency wallet address
     */
    walletAddress?: string;
    /**
     * Duplicate status [sys]
     */
    duplicate?: boolean;
    /**
     * Duplicate date [sys]
     */
    duplicateDate?: string | null;
    /**
     * Withdrawn status [sys]
     */
    withdrawn?: boolean;
    /**
     * Withdrawn date [sys]
     */
    withdrawnDate?: string | null;
    /**
     * FlexFields JSON representation [sys]
     */
    flexFields?: any;
    /**
     * Beneficiary phone number valid [sys]
     */
    phoneNoValid?: boolean | null;
    /**
     * Beneficiary phone number alternative valid [sys]
     */
    phoneNoAlternativeValid?: boolean | null;
    /**
     * Enrolled in nutrition program [sys]
     */
    enrolledInNutritionProgramme?: boolean | null;
    /**
     * Deduplication golden record status [sys]
     *
     * * `DUPLICATE` - Duplicate
     * * `NEEDS_ADJUDICATION` - Needs Adjudication
     * * `NOT_PROCESSED` - Not Processed
     * * `POSTPONE` - Postpone
     * * `UNIQUE` - Unique
     */
    deduplicationGoldenRecordStatus?: DeduplicationGoldenRecordStatusEnum;
    /**
     * Deduplication golden record status [sys]
     *
     * * `DUPLICATE` - Duplicate
     * * `NEEDS_ADJUDICATION` - Needs Adjudication
     * * `NOT_PROCESSED` - Not Processed
     * * `POSTPONE` - Postpone
     * * `UNIQUE` - Unique
     */
    biometricDeduplicationGoldenRecordStatus?: BiometricDeduplicationGoldenRecordStatusEnum;
    /**
     * Deduplication batch status [sys]
     *
     * * `DUPLICATE_IN_BATCH` - Duplicate in batch
     * * `NOT_PROCESSED` - Not Processed
     * * `SIMILAR_IN_BATCH` - Similar in batch
     * * `UNIQUE_IN_BATCH` - Unique in batch
     */
    biometricDeduplicationBatchStatus?: BiometricDeduplicationBatchStatusEnum;
    /**
     * Deduplication golden record results [sys]
     */
    biometricDeduplicationGoldenRecordResults?: any;
    /**
     * Deduplication batch results [sys]
     */
    biometricDeduplicationBatchResults?: any;
    /**
     * Imported individual ID [sys]
     */
    importedIndividualId?: string | null;
    /**
     * Sanction list possible match [sys]
     */
    sanctionListPossibleMatch?: boolean;
    /**
     * Sanction list confirmed match [sys]
     */
    sanctionListConfirmedMatch?: boolean;
    /**
     * Kobo asset ID, Xlsx row ID, Aurora registration ID [sys]
     */
    detailId?: string | null;
    /**
     * Beneficiary Program Registration ID [sys]
     */
    programRegistrationId?: string | null;
    /**
     * Age at registration [sys]
     */
    ageAtRegistration?: number | null;
    /**
     * Original unicef_id [sys]
     */
    originUnicefId?: string | null;
    /**
     * Migration status [sys]
     */
    isMigrationHandled?: boolean;
    /**
     * Migrated at [sys]
     */
    migratedAt?: string | null;
    /**
     * Collection of individual representations
     */
    individualCollection?: number | null;
    /**
     * If this individual was copied from another individual, this field will contain the individual it was copied from.
     */
    copiedFrom?: string | null;
};

