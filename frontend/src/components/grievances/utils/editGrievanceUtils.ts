import camelCase from 'lodash/camelCase';
import React from 'react';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../utils/constants';
import {
  thingForSpecificGrievanceType,
  camelizeArrayObjects,
} from '../../../utils/utils';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { AddIndividualDataChange } from '../AddIndividualDataChange';
import { EditIndividualDataChange } from '../EditIndividualDataChange/EditIndividualDataChange';
import { EditHouseholdDataChange } from '../EditHouseholdDataChange/EditHouseholdDataChange';

interface EditValuesTypes {
  priority?: number;
  urgency?: number;
  description?: string;
  assignedTo?: string;
  issueType?: string | number;
  category?: string | number;
  language: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  admin: any;
  area: string;
  selectedHousehold?;
  selectedIndividual?;
  selectedPaymentRecords: string[];
  paymentRecord?: string;
  selectedRelatedTickets: string[];
  individualData?;
  householdDataUpdateFields?;
  partner?;
  comments?;
  programme?;
  documentation?;
  documentationToUpdate?;
  documentationToDelete?;
}

function prepareInitialValueAddIndividual(
  initialValuesArg,
  ticket: GrievanceTicketQuery['grievanceTicket'],
): EditValuesTypes {
  const initialValues = initialValuesArg;
  initialValues.selectedHousehold = ticket.household;
  const individualData = {
    ...ticket.addIndividualTicketDetails.individualData,
  };
  const flexFields = individualData.flex_fields;
  delete individualData.flex_fields;
  initialValues.individualData = Object.entries(individualData).reduce(
    (previousValue, currentValue: [string, { value: string }]) => {
      // eslint-disable-next-line no-param-reassign,prefer-destructuring
      previousValue[camelCase(currentValue[0])] = currentValue[1];
      return previousValue;
    },
    {},
  );
  initialValues.individualData.flexFields = Object.entries(flexFields).reduce(
    (previousValue, currentValue: [string, { value: string }]) => {
      // eslint-disable-next-line no-param-reassign,prefer-destructuring
      previousValue[camelCase(currentValue[0])] = currentValue[1];
      return previousValue;
    },
    {},
  );
  return initialValues;
}
function prepareInitialValueEditIndividual(
  initialValuesArg,
  ticket: GrievanceTicketQuery['grievanceTicket'],
): EditValuesTypes {
  const initialValues = initialValuesArg;
  initialValues.selectedIndividual = ticket.individual;
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  const documents = individualData?.documents;
  const documentsToRemove = individualData.documents_to_remove;
  const documentsEdited = individualData?.documents_to_edit;
  const identities = individualData?.identities;
  const identitiesToRemove = individualData?.identities_to_remove;
  const identitiesEdited = individualData?.identities_to_edit;
  const paymentChannels = individualData?.payment_channels;
  const paymentChannelsToRemove = individualData?.payment_channels_to_remove;
  const paymentChannelsEdited = individualData?.payment_channels_to_edit;
  const flexFields = individualData.flex_fields;
  delete individualData.documents;
  delete individualData.documents_to_remove;
  delete individualData.documents_to_edit;
  delete individualData.identities;
  delete individualData.identities_to_remove;
  delete individualData.identities_to_edit;
  delete individualData.payment_channels;
  delete individualData.payment_channels_to_remove;
  delete individualData.payment_channels_to_edit;
  delete individualData.previous_payment_channels;
  delete individualData.previous_documents;
  delete individualData.previous_identities;
  delete individualData.flex_fields;
  const individualDataArray = Object.entries(individualData).map(
    (entry: [string, { value: string }]) => ({
      fieldName: entry[0],
      fieldValue: entry[1].value,
    }),
  );
  const flexFieldsArray = Object.entries(flexFields).map(
    (entry: [string, { value: string }]) => ({
      fieldName: entry[0],
      fieldValue: entry[1].value,
    }),
  );
  initialValues.individualDataUpdateFields = [
    ...individualDataArray,
    ...flexFieldsArray,
  ];
  initialValues.individualDataUpdateFieldsDocuments = (documents || []).map(
    (item) => item.value,
  );
  initialValues.individualDataUpdateDocumentsToRemove = (
    documentsToRemove || []
  ).map((item) => item.value);
  initialValues.individualDataUpdateFieldsIdentities = (identities || []).map(
    (item) => item.value,
  );
  initialValues.individualDataUpdateIdentitiesToRemove = (
    identitiesToRemove || []
  ).map((item) => item.value);
  initialValues.individualDataUpdateDocumentsToEdit = (
    documentsEdited || []
  ).map((item) => item.value);
  initialValues.individualDataUpdateIdentitiesToEdit = (
    identitiesEdited || []
  ).map((item) => item.value);
  initialValues.individualDataUpdateFieldsPaymentChannels = (
    camelizeArrayObjects(paymentChannels) || []
  ).map((item) => item.value);
  initialValues.individualDataUpdatePaymentChannelsToRemove = (
    camelizeArrayObjects(paymentChannelsToRemove) || []
  ).map((item) => item.value);
  initialValues.individualDataUpdatePaymentChannelsToEdit = (
    camelizeArrayObjects(paymentChannelsEdited) || []
  ).map((item) => item.value);
  return initialValues;
}
function prepareInitialValueEditHousehold(
  initialValuesArg,
  ticket: GrievanceTicketQuery['grievanceTicket'],
): EditValuesTypes {
  const initialValues = initialValuesArg;
  initialValues.selectedHousehold = ticket.household;
  const householdData = {
    ...ticket.householdDataUpdateTicketDetails.householdData,
  };
  const flexFields = householdData.flex_fields;
  delete householdData.flex_fields;
  const householdDataArray = Object.entries(householdData).map(
    (entry: [string, { value: string }]) => ({
      fieldName: entry[0],
      fieldValue: entry[1].value,
    }),
  );
  const flexFieldsArray = Object.entries(flexFields).map(
    (entry: [string, { value: string }]) => ({
      fieldName: entry[0],
      fieldValue: entry[1].value,
    }),
  );
  initialValues.householdDataUpdateFields = [
    ...householdDataArray,
    ...flexFieldsArray,
  ];
  return initialValues;
}

const prepareInitialValueDict = {
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: {
    [GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL]: prepareInitialValueAddIndividual,
    [GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL]: prepareInitialValueEditIndividual,
    [GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD]: prepareInitialValueEditHousehold,
  },
};

export function prepareInitialValues(
  ticket: GrievanceTicketQuery['grievanceTicket'],
): EditValuesTypes {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let initialValues: EditValuesTypes = {
    priority: ticket.priority,
    urgency: ticket.urgency,
    partner: ticket.partner?.id,
    comments: ticket.comments,
    programme: ticket.programme?.id,
    description: ticket.description || '',
    assignedTo: ticket?.assignedTo?.id || '',
    category: ticket.category || null,
    language: ticket.language || '',
    admin: ticket.admin2 ? { node: ticket.admin2 } : null,
    area: ticket.area || '',
    selectedHousehold: ticket.household || null,
    selectedIndividual: ticket.individual || null,
    issueType: ticket.issueType || null,
    paymentRecord: ticket?.paymentRecord?.id || null,
    selectedPaymentRecords: ticket?.paymentRecord?.id
      ? [ticket.paymentRecord.id]
      : [],
    selectedRelatedTickets: ticket.relatedTickets.map(
      (relatedTicket) => relatedTicket.id,
    ),
    documentation: null,
    documentationToUpdate: null,
    documentationToDelete: null,
  };
  const prepareInitialValueFunction = thingForSpecificGrievanceType(
    ticket,
    prepareInitialValueDict,
    (initialValue) => initialValue,
  );
  initialValues = prepareInitialValueFunction(
    initialValues,
    ticket,
  ) as EditValuesTypes;
  return initialValues;
}

export const EmptyComponent = (): React.ReactElement => null;
export const dataChangeComponentDict = {
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: {
    [GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL]: AddIndividualDataChange,
    [GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL]: EditIndividualDataChange,
    [GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD]: EditHouseholdDataChange,
  },
};

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function preparePositiveFeedbackVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          category: {
            positiveFeedbackTicketExtras: {
              household: values.selectedHousehold?.id,
              individual: values.selectedIndividual?.id,
            },
          },
        },
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareNegativeFeedbackVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          category: {
            negativeFeedbackTicketExtras: {
              household: values.selectedHousehold?.id,
              individual: values.selectedIndividual?.id,
            },
          },
        },
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareReferralVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          category: {
            referralTicketExtras: {
              household: values.selectedHousehold?.id,
              individual: values.selectedIndividual?.id,
            },
          },
        },
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareGrievanceComplaintVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        issueType: values.issueType,
        linkedTickets: values.selectedRelatedTickets,
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareSesitiveVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareAddIndividualVariables(requiredVariables, values) {
  let { flexFields } = values.individualData;
  if (flexFields) {
    flexFields = { ...flexFields };
    for (const [key, value] of Object.entries(flexFields)) {
      if (value === '') {
        delete flexFields[key];
      }
    }
  }
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          addIndividualIssueTypeExtras: {
            individualData: { ...values.individualData, flexFields },
          },
        },
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareDeleteIndividualVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareEditIndividualVariables(requiredVariables, values) {
  const individualData = values.individualDataUpdateFields
    .filter((item) => item.fieldName && !item.isFlexField)
    .reduce((prev, current) => {
      // eslint-disable-next-line no-param-reassign
      prev[camelCase(current.fieldName)] = current.fieldValue;
      return prev;
    }, {});
  const flexFields = values.individualDataUpdateFields
    .filter((item) => item.fieldName && item.isFlexField)
    .reduce((prev, current) => {
      // eslint-disable-next-line no-param-reassign
      prev[camelCase(current.fieldName)] = current.fieldValue;
      return prev;
    }, {});
  individualData.flexFields = flexFields;
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          individualDataUpdateIssueTypeExtras: {
            individualData: {
              ...individualData,
              documents: values.individualDataUpdateFieldsDocuments,
              documentsToRemove: values.individualDataUpdateDocumentsToRemove,
              documentsToEdit: values.individualDataUpdateDocumentsToEdit,
              identities: values.individualDataUpdateFieldsIdentities,
              identitiesToRemove: values.individualDataUpdateIdentitiesToRemove,
              identitiesToEdit: values.individualDataUpdateIdentitiesToEdit,
              paymentChannels: values.individualDataUpdateFieldsPaymentChannels,
              paymentChannelsToRemove:
                values.individualDataUpdatePaymentChannelsToRemove,
              paymentChannelsToEdit:
                values.individualDataUpdatePaymentChannelsToEdit,
            },
          },
        },
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareEditHouseholdVariables(requiredVariables, values) {
  const householdData = values.householdDataUpdateFields
    .filter((item) => item.fieldName && !item.isFlexField)
    .reduce((prev, current) => {
      // eslint-disable-next-line no-param-reassign
      prev[camelCase(current.fieldName)] = current.fieldValue;
      return prev;
    }, {});
  const flexFields = values.householdDataUpdateFields
    .filter((item) => item.fieldName && item.isFlexField)
    .reduce((prev, current) => {
      // eslint-disable-next-line no-param-reassign
      prev[current.fieldName] = current.fieldValue;
      return prev;
    }, {});
  householdData.flexFields = flexFields;
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          householdDataUpdateIssueTypeExtras: {
            householdData,
          },
        },
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareDefaultVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
      },
    },
  };
}

export const prepareVariablesDict = {
  [GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK]: prepareNegativeFeedbackVariables,
  [GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK]: preparePositiveFeedbackVariables,
  [GRIEVANCE_CATEGORIES.REFERRAL]: prepareReferralVariables,
  [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: prepareGrievanceComplaintVariables,
  [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: prepareSesitiveVariables,
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: {
    [GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL]: prepareAddIndividualVariables,
    [GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL]: prepareDeleteIndividualVariables,
    [GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL]: prepareEditIndividualVariables,
    [GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD]: prepareEditHouseholdVariables,
  },
};
const grievanceTypeIssueTypeDict = {
  [GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK]: false,
  [GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK]: false,
  [GRIEVANCE_CATEGORIES.REFERRAL]: false,
  [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: false,
  [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: 'IGNORE',
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: true,
};
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function prepareVariables(businessArea, values, ticket) {
  const requiredVariables = {
    ticketId: ticket.id,
    description: values.description,
    assignedTo: values.assignedTo,
    language: values.language,
    admin: values?.admin?.node?.pCode,
    area: values.area,
    household: values.selectedHousehold?.id,
    individual: values.selectedIndividual?.id,
    priority: values.priority,
    urgency: values.urgency,
    partner: values.partner,
    comments: values.comments,
    programme: values.programme,
    paymentRecord: values.selectedPaymentRecords[0] || null,
    documentation: values.documentation || null,
    documentationToUpdate: values.documentationToUpdate || null,
    documentationToDelete: values.documentationToDelete || null,
  };
  const prepareFunction = thingForSpecificGrievanceType(
    values,
    prepareVariablesDict,
    prepareDefaultVariables,
    grievanceTypeIssueTypeDict,
  );
  return prepareFunction(requiredVariables, values);
}
