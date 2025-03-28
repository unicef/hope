/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
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
    first_registration_date?: string;
    last_registration_date?: string;
    readonly household: string;
    role?: string;
    observed_disability?: string;
    country_origin?: string;
    marital_status?: string;
    documents?: Array<Document>;
    birth_date: string;
    rdi_merge_status?: RdiMergeStatusEnum;
    is_removed?: boolean;
    removed_date?: string | null;
    last_sync_at?: string | null;
    internal_data?: any;
    /**
     * Individual ID
     */
    individual_id?: string;
    /**
     * Photo
     */
    photo?: string;
    /**
     * Full Name of the Beneficiary
     */
    full_name: string;
    /**
     * First name of the Beneficiary
     */
    given_name?: string;
    /**
     * Middle name of the Beneficiary
     */
    middle_name?: string;
    /**
     * Last name of the Beneficiary
     */
    family_name?: string;
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
    estimated_birth_date?: boolean;
    /**
     * Beneficiary phone number
     */
    phone_no?: string;
    /**
     * Beneficiary phone number alternative
     */
    phone_no_alternative?: string;
    /**
     * Beneficiary email address
     */
    email?: string;
    /**
     * Beneficiary contact phone number
     */
    payment_delivery_phone_no?: string | null;
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
    work_status?: WorkStatusEnum;
    /**
     * Pregnant status
     */
    pregnant?: boolean | null;
    /**
     * Child is female and Head of Household flag
     */
    fchild_hoh?: boolean;
    /**
     * Child is Head of Household flag
     */
    child_hoh?: boolean;
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
    disability_certificate_picture?: string | null;
    /**
     * Seeing disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    seeing_disability?: SeeingDisabilityEnum;
    /**
     * Hearing disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    hearing_disability?: HearingDisabilityEnum;
    /**
     * Physical disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    physical_disability?: PhysicalDisabilityEnum;
    /**
     * Memory disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    memory_disability?: MemoryDisabilityEnum;
    /**
     * Selfcare disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    selfcare_disability?: SelfcareDisabilityEnum;
    /**
     * Comms disability
     *
     * * `` - None
     * * `LOT_DIFFICULTY` - A lot of difficulty
     * * `CANNOT_DO` - Cannot do at all
     * * `SOME_DIFFICULTY` - Some difficulty
     */
    comms_disability?: CommsDisabilityEnum;
    /**
     * Who answers phone number
     */
    who_answers_phone?: string;
    /**
     * Who answers alternative phone number
     */
    who_answers_alt_phone?: string;
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
    preferred_language?: PreferredLanguageEnum | null;
    /**
     * Relationship confirmed status
     */
    relationship_confirmed?: boolean;
    /**
     * Cryptocurrency wallet name
     */
    wallet_name?: string;
    /**
     * Cryptocurrency blockchain name
     */
    blockchain_name?: string;
    /**
     * Cryptocurrency wallet address
     */
    wallet_address?: string;
    /**
     * Duplicate status [sys]
     */
    duplicate?: boolean;
    /**
     * Duplicate date [sys]
     */
    duplicate_date?: string | null;
    /**
     * Withdrawn status [sys]
     */
    withdrawn?: boolean;
    /**
     * Withdrawn date [sys]
     */
    withdrawn_date?: string | null;
    /**
     * FlexFields JSON representation [sys]
     */
    flex_fields?: any;
    /**
     * Beneficiary phone number valid [sys]
     */
    phone_no_valid?: boolean | null;
    /**
     * Beneficiary phone number alternative valid [sys]
     */
    phone_no_alternative_valid?: boolean | null;
    /**
     * Enrolled in nutrition program [sys]
     */
    enrolled_in_nutrition_programme?: boolean | null;
    /**
     * Deduplication golden record status [sys]
     *
     * * `DUPLICATE` - Duplicate
     * * `NEEDS_ADJUDICATION` - Needs Adjudication
     * * `NOT_PROCESSED` - Not Processed
     * * `POSTPONE` - Postpone
     * * `UNIQUE` - Unique
     */
    deduplication_golden_record_status?: DeduplicationGoldenRecordStatusEnum;
    /**
     * Deduplication golden record status [sys]
     *
     * * `DUPLICATE` - Duplicate
     * * `NEEDS_ADJUDICATION` - Needs Adjudication
     * * `NOT_PROCESSED` - Not Processed
     * * `POSTPONE` - Postpone
     * * `UNIQUE` - Unique
     */
    biometric_deduplication_golden_record_status?: BiometricDeduplicationGoldenRecordStatusEnum;
    /**
     * Deduplication batch status [sys]
     *
     * * `DUPLICATE_IN_BATCH` - Duplicate in batch
     * * `NOT_PROCESSED` - Not Processed
     * * `SIMILAR_IN_BATCH` - Similar in batch
     * * `UNIQUE_IN_BATCH` - Unique in batch
     */
    biometric_deduplication_batch_status?: BiometricDeduplicationBatchStatusEnum;
    /**
     * Deduplication golden record results [sys]
     */
    biometric_deduplication_golden_record_results?: any;
    /**
     * Deduplication batch results [sys]
     */
    biometric_deduplication_batch_results?: any;
    /**
     * Imported individual ID [sys]
     */
    imported_individual_id?: string | null;
    /**
     * Sanction list possible match [sys]
     */
    sanction_list_possible_match?: boolean;
    /**
     * Sanction list confirmed match [sys]
     */
    sanction_list_confirmed_match?: boolean;
    /**
     * Kobo asset ID, Xlsx row ID, Aurora registration ID [sys]
     */
    detail_id?: string | null;
    /**
     * Beneficiary Program Registration ID [sys]
     */
    program_registration_id?: string | null;
    /**
     * Age at registration [sys]
     */
    age_at_registration?: number | null;
    /**
     * Original unicef_id [sys]
     */
    origin_unicef_id?: string | null;
    /**
     * Migration status [sys]
     */
    is_migration_handled?: boolean;
    /**
     * Migrated at [sys]
     */
    migrated_at?: string | null;
    /**
     * Collection of individual representations
     */
    individual_collection?: number | null;
    /**
     * If this individual was copied from another individual, this field will contain the individual it was copied from.
     */
    copied_from?: string | null;
};

