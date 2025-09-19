/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BiometricDeduplicationBatchStatusEnum } from './BiometricDeduplicationBatchStatusEnum';
import type { BiometricDeduplicationGoldenRecordStatusEnum } from './BiometricDeduplicationGoldenRecordStatusEnum';
import type { DeduplicationBatchStatusEnum } from './DeduplicationBatchStatusEnum';
import type { DeduplicationEngineSimilarityPairIndividual } from './DeduplicationEngineSimilarityPairIndividual';
import type { DeduplicationGoldenRecordStatusEnum } from './DeduplicationGoldenRecordStatusEnum';
import type { DeduplicationResult } from './DeduplicationResult';
import type { IndividualListHousehold } from './IndividualListHousehold';
import type { ProgramSmall } from './ProgramSmall';
import type { RelationshipEnum } from './RelationshipEnum';
import type { SexEnum } from './SexEnum';
export type IndividualList = {
    readonly id: string;
    unicefId: string | null;
    /**
     * Full Name of the Beneficiary
     */
    fullName: string;
    household: IndividualListHousehold;
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
    readonly role: string;
    relationshipDisplay: string;
    /**
     * Beneficiary date of birth
     */
    birthDate: string;
    /**
     * Deduplication batch status [sys]
     *
     * * `DUPLICATE_IN_BATCH` - Duplicate in batch
     * * `NOT_PROCESSED` - Not Processed
     * * `SIMILAR_IN_BATCH` - Similar in batch
     * * `UNIQUE_IN_BATCH` - Unique in batch
     */
    deduplicationBatchStatus?: DeduplicationBatchStatusEnum;
    deduplicationBatchStatusDisplay: string;
    /**
     * Deduplication batch status [sys]
     *
     * * `DUPLICATE_IN_BATCH` - Duplicate in batch
     * * `NOT_PROCESSED` - Not Processed
     * * `SIMILAR_IN_BATCH` - Similar in batch
     * * `UNIQUE_IN_BATCH` - Unique in batch
     */
    biometricDeduplicationBatchStatus?: BiometricDeduplicationBatchStatusEnum;
    biometricDeduplicationBatchStatusDisplay: string;
    readonly deduplicationBatchResults: Array<DeduplicationResult>;
    readonly biometricDeduplicationBatchResults: Array<DeduplicationEngineSimilarityPairIndividual>;
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
    deduplicationGoldenRecordStatusDisplay: string;
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
    biometricDeduplicationGoldenRecordStatusDisplay: string;
    readonly deduplicationGoldenRecordResults: Array<DeduplicationResult>;
    readonly biometricDeduplicationGoldenRecordResults: Array<DeduplicationEngineSimilarityPairIndividual>;
    program: ProgramSmall;
    /**
     * Last registration date [sys]
     */
    lastRegistrationDate: string;
};

