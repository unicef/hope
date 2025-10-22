/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateAccount } from './CreateAccount';
import type { IndividualDocument } from './IndividualDocument';
import type { IndividualIdentityGT } from './IndividualIdentityGT';
export type AddIndividualData = {
    fullName: string;
    givenName?: string;
    middleName?: string;
    familyName?: string;
    sex: string;
    birthDate: string;
    estimatedBirthDate: boolean;
    maritalStatus?: string;
    phoneNo?: string;
    phoneNoAlternative?: string;
    email?: string;
    relationship: string;
    disability?: string;
    workStatus?: string;
    enrolledInNutritionProgramme?: boolean;
    pregnant?: boolean;
    observedDisability?: Array<string>;
    seeingDisability?: string;
    hearingDisability?: string;
    physicalDisability?: string;
    memoryDisability?: string;
    selfcareDisability?: string;
    commsDisability?: string;
    whoAnswersPhone?: string;
    whoAnswersAltPhone?: string;
    businessArea?: string;
    documents?: Array<IndividualDocument>;
    identities?: Array<IndividualIdentityGT>;
    accounts?: Array<CreateAccount>;
    preferredLanguage?: string;
    flexFields?: any;
    paymentDeliveryPhoneNo?: string;
    blockchainName?: string;
    walletAddress?: string;
    walletName?: string;
};

