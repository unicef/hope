/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateAccount } from './CreateAccount';
import type { EditAccount } from './EditAccount';
import type { EditIndividualDocument } from './EditIndividualDocument';
import type { EditIndividualIdentity } from './EditIndividualIdentity';
import type { IndividualDocument } from './IndividualDocument';
import type { IndividualIdentityGT } from './IndividualIdentityGT';
export type IndividualUpdateData = {
    status?: string;
    fullName?: string;
    givenName?: string;
    middleName?: string;
    familyName?: string;
    sex?: string;
    birthDate?: string;
    estimatedBirthDate?: boolean;
    maritalStatus?: string | null;
    phoneNo?: string;
    phoneNoAlternative?: string;
    email?: string;
    relationship?: string;
    disability?: string;
    workStatus?: string;
    enrolledInNutritionProgramme?: boolean;
    pregnant?: boolean | null;
    observedDisability?: Array<string>;
    seeingDisability?: string;
    hearingDisability?: string;
    physicalDisability?: string;
    memoryDisability?: string;
    selfcareDisability?: string;
    commsDisability?: string;
    whoAnswersPhone?: string;
    whoAnswersAltPhone?: string;
    documents?: Array<IndividualDocument>;
    documentsToRemove?: Array<string>;
    documentsToEdit?: Array<EditIndividualDocument>;
    identities?: Array<IndividualIdentityGT>;
    identitiesToRemove?: Array<number>;
    identitiesToEdit?: Array<EditIndividualIdentity>;
    accounts?: Array<CreateAccount>;
    accountsToEdit?: Array<EditAccount>;
    preferredLanguage?: string;
    flexFields?: any;
    paymentDeliveryPhoneNo?: string;
    blockchainName?: string;
    walletAddress?: string;
    walletName?: string;
    /**
     * People update
     */
    consent?: string | null;
    /**
     * People update
     */
    residenceStatus?: string;
    /**
     * People update
     */
    countryOrigin?: string;
    /**
     * People update
     */
    country?: string;
    /**
     * People update
     */
    address?: string;
    /**
     * People update
     */
    village?: string;
    /**
     * People update
     */
    currency?: string;
    /**
     * People update
     */
    unhcrId?: string;
    /**
     * People update
     */
    nameEnumerator?: string;
    /**
     * People update
     */
    orgEnumerator?: string;
    /**
     * People update
     */
    orgNameEnumerator?: string;
    /**
     * People update
     */
    registrationMethod?: string;
    /**
     * People update
     */
    adminAreaTitle?: string;
};

