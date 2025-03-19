/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Admin1Enum } from './Admin1Enum';
import type { Admin2Enum } from './Admin2Enum';
import type { Admin3Enum } from './Admin3Enum';
import type { Admin4Enum } from './Admin4Enum';
import type { BlankEnum } from './BlankEnum';
import type { CollectIndividualDataEnum } from './CollectIndividualDataEnum';
import type { CommsDisabilityEnum } from './CommsDisabilityEnum';
import type { CountryEnum } from './CountryEnum';
import type { CountryOriginEnum } from './CountryOriginEnum';
import type { DeduplicationGoldenRecordStatusEnum } from './DeduplicationGoldenRecordStatusEnum';
import type { DisabilityEnum } from './DisabilityEnum';
import type { Document } from './Document';
import type { HearingDisabilityEnum } from './HearingDisabilityEnum';
import type { MemoryDisabilityEnum } from './MemoryDisabilityEnum';
import type { NullEnum } from './NullEnum';
import type { PhysicalDisabilityEnum } from './PhysicalDisabilityEnum';
import type { PreferredLanguageEnum } from './PreferredLanguageEnum';
import type { PushPeopleTypeEnum } from './PushPeopleTypeEnum';
import type { RdiMergeStatusEnum } from './RdiMergeStatusEnum';
import type { RelationshipEnum } from './RelationshipEnum';
import type { ResidenceStatusEnum } from './ResidenceStatusEnum';
import type { SeeingDisabilityEnum } from './SeeingDisabilityEnum';
import type { SelfcareDisabilityEnum } from './SelfcareDisabilityEnum';
import type { SexEnum } from './SexEnum';
import type { WorkStatusEnum } from './WorkStatusEnum';
export type PushPeople = {
    first_registration_date?: string;
    last_registration_date?: string;
    observed_disability?: string;
    marital_status?: string;
    documents?: Array<Document>;
    birth_date: string;
    type: (PushPeopleTypeEnum | BlankEnum);
    country_origin?: CountryOriginEnum;
    country: CountryEnum;
    collect_individual_data: (CollectIndividualDataEnum | BlankEnum);
    residence_status: (ResidenceStatusEnum | BlankEnum);
    village?: string | null;
    phone_no?: string | null;
    phone_no_alternative?: string | null;
    admin1?: (Admin1Enum | BlankEnum | NullEnum) | null;
    admin2?: (Admin2Enum | BlankEnum | NullEnum) | null;
    admin3?: (Admin3Enum | BlankEnum | NullEnum) | null;
    admin4?: (Admin4Enum | BlankEnum | NullEnum) | null;
    rdi_merge_status?: RdiMergeStatusEnum;
    is_original?: boolean;
    is_removed?: boolean;
    removed_date?: string | null;
    last_sync_at?: string | null;
    /**
     * record revision number
     */
    version?: number;
    duplicate?: boolean;
    duplicate_date?: string | null;
    withdrawn?: boolean;
    withdrawn_date?: string | null;
    individual_id?: string;
    photo?: string;
    full_name: string;
    given_name?: string;
    middle_name?: string;
    family_name?: string;
    sex: SexEnum;
    estimated_birth_date?: boolean;
    phone_no_valid?: boolean | null;
    phone_no_alternative_valid?: boolean | null;
    email?: string;
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
    relationship?: (RelationshipEnum | BlankEnum);
    work_status?: (WorkStatusEnum | BlankEnum);
    flex_fields?: any;
    user_fields?: any;
    enrolled_in_nutrition_programme?: boolean | null;
    deduplication_golden_record_status?: DeduplicationGoldenRecordStatusEnum;
    imported_individual_id?: string | null;
    sanction_list_possible_match?: boolean;
    sanction_list_confirmed_match?: boolean;
    pregnant?: boolean | null;
    disability?: DisabilityEnum;
    disability_certificate_picture?: string | null;
    seeing_disability?: (SeeingDisabilityEnum | BlankEnum);
    hearing_disability?: (HearingDisabilityEnum | BlankEnum);
    physical_disability?: (PhysicalDisabilityEnum | BlankEnum);
    memory_disability?: (MemoryDisabilityEnum | BlankEnum);
    selfcare_disability?: (SelfcareDisabilityEnum | BlankEnum);
    comms_disability?: (CommsDisabilityEnum | BlankEnum);
    who_answers_phone?: string;
    who_answers_alt_phone?: string;
    fchild_hoh?: boolean;
    child_hoh?: boolean;
    registration_id?: string | null;
    program_registration_id?: string | null;
    preferred_language?: (PreferredLanguageEnum | BlankEnum | NullEnum) | null;
    relationship_confirmed?: boolean;
    age_at_registration?: number | null;
    wallet_name?: string;
    blockchain_name?: string;
    wallet_address?: string;
    origin_unicef_id?: string | null;
    is_migration_handled?: boolean;
    migrated_at?: string | null;
    mis_unicef_id?: string | null;
    vector_column?: string | null;
    individual_collection?: number | null;
    program?: string | null;
    /**
     * If this individual was copied from another individual, this field will contain the individual it was copied from.
     */
    copied_from?: string | null;
};

