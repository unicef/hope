/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HouseholdSimple } from './HouseholdSimple';
import type { RelationshipEnum } from './RelationshipEnum';
import type { SexEnum } from './SexEnum';
export type IndividualList = {
    id: string;
    unicef_id?: string | null;
    /**
     * Full Name of the Beneficiary
     */
    full_name: string;
    household: HouseholdSimple;
    readonly status: string;
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
    readonly age: number;
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
};

