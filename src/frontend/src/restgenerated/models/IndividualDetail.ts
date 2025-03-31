/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CommsDisabilityEnum } from './CommsDisabilityEnum';
import type { DisabilityEnum } from './DisabilityEnum';
import type { HearingDisabilityEnum } from './HearingDisabilityEnum';
import type { HouseholdSimple } from './HouseholdSimple';
import type { MaritalStatusEnum } from './MaritalStatusEnum';
import type { MemoryDisabilityEnum } from './MemoryDisabilityEnum';
import type { ObservedDisabilityEnum } from './ObservedDisabilityEnum';
import type { PhysicalDisabilityEnum } from './PhysicalDisabilityEnum';
import type { PreferredLanguageEnum } from './PreferredLanguageEnum';
import type { RegistrationDataImport } from './RegistrationDataImport';
import type { RelationshipEnum } from './RelationshipEnum';
import type { SeeingDisabilityEnum } from './SeeingDisabilityEnum';
import type { SelfcareDisabilityEnum } from './SelfcareDisabilityEnum';
import type { SexEnum } from './SexEnum';
import type { WorkStatusEnum } from './WorkStatusEnum';
export type IndividualDetail = {
    id: string;
    unicef_id?: string | null;
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
    readonly age: number;
    /**
     * Beneficiary date of birth
     */
    birth_date: string;
    /**
     * Estimated birth date flag
     */
    estimated_birth_date?: boolean;
    /**
     * Beneficiary marital status
     *
     * * `` - None
     * * `DIVORCED` - Divorced
     * * `MARRIED` - Married
     * * `SEPARATED` - Separated
     * * `SINGLE` - Single
     * * `WIDOWED` - Widowed
     */
    marital_status?: MaritalStatusEnum;
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
    household: HouseholdSimple;
    readonly role: string;
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
    registration_data_import: RegistrationDataImport;
    readonly import_id: string;
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
    readonly roles_in_households: Record<string, any>;
    /**
     * Observed disability status
     *
     * * `NONE` - None
     * * `SEEING` - Difficulty seeing (even if wearing glasses)
     * * `HEARING` - Difficulty hearing (even if using a hearing aid)
     * * `WALKING` - Difficulty walking or climbing steps
     * * `MEMORY` - Difficulty remembering or concentrating
     * * `SELF_CARE` - Difficulty with self care (washing, dressing)
     * * `COMMUNICATING` - Difficulty communicating (e.g understanding or being understood)
     */
    observed_disability?: ObservedDisabilityEnum;
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
     * Disability status
     *
     * * `disabled` - disabled
     * * `not disabled` - not disabled
     */
    disability?: DisabilityEnum;
    readonly documents: Record<string, any>;
    readonly identities: Record<string, any>;
    readonly bank_account_info: Record<string, any>;
    readonly delivery_mechanisms_data: Record<string, any>;
    /**
     * Beneficiary email address
     */
    email?: string;
    /**
     * Beneficiary phone number
     */
    phone_no?: string;
    /**
     * Beneficiary phone number alternative
     */
    phone_no_alternative?: string;
    readonly sanction_list_last_check: string | null;
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
    readonly status: string;
    readonly flex_fields: Record<string, any>;
    readonly linked_grievances: Record<string, any>;
};

