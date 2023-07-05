import camelCase from 'lodash/camelCase';
import React from 'react';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../utils/constants';
import {
  camelizeArrayObjects,
  thingForSpecificGrievanceType,
} from '../../../utils/utils';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { AddIndividualDataChange } from '../AddIndividualDataChange';
import { EditHouseholdDataChange } from '../EditHouseholdDataChange/EditHouseholdDataChange';
import { EditIndividualDataChange } from '../EditIndividualDataChange/EditIndividualDataChange';

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
  selectedLinkedTickets: string[];
  individualData?;
  householdDataUpdateFields?;
  partner?;
  comments?;
  program?;
  documentation?;
  documentationToUpdate?;
  documentationToDelete?;
}

function prepareInitialValueAddIndividual(
  initialValuesArg: EditValuesTypes,
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
      previousValue[camelCase(currentValue[0])] = currentValue[1].value;
      return previousValue;
    },
    {} as EditValuesTypes['individualData'],
  );
  initialValues.individualData.flexFields = Object.entries(flexFields).reduce(
    (previousValue, currentValue: [string, { value: string }]) => {
      // eslint-disable-next-line no-param-reassign,prefer-destructuring
      previousValue[camelCase(currentValue[0])] = currentValue[1].value;
      return previousValue;
    },
    {} as EditValuesTypes['individualData']['flexFields'],
  );
  return initialValues;
}

//eslint-disable-next-line
function prepareInitialValueEditIndividual(initialValues, ticket) {
  const {
    individual,
    individualDataUpdateTicketDetails: { individualData },
  } = ticket;

  const initialValuesCopy = { ...initialValues }; // make a copy to avoid modifying the original object
  initialValuesCopy.selectedIndividual = individual;

  const {
    documents,
    documents_to_remove: documentsToRemove,
    documents_to_edit: documentsToEdit,
    identities,
    identities_to_remove: identitiesToRemove,
    identities_to_edit: identitiesToEdit,
    payment_channels: paymentChannels,
    payment_channels_to_remove: paymentChannelsToRemove,
    payment_channels_to_edit: paymentChannelsToEdit,
    ...rest
  } = individualData;

  delete rest.documents;
  delete rest.flex_fields;
  delete rest.previous_payment_channels;
  delete rest.previous_documents;
  delete rest.previous_identities;

  interface Field {
    value: string;
  }

  const individualDataArray = Object.entries(rest)
    .map(([fieldName, field]: [string, Field]) => {
      if (field.value !== undefined) {
        return { fieldName, fieldValue: field.value };
      }
      return null;
    })
    .filter((field) => field !== null);

  const flexFieldsArray = Object.entries(individualData.flex_fields)
    .map(([fieldName, field]: [string, Field]) => {
      if (field.value !== undefined) {
        return { fieldName, fieldValue: field.value };
      }
      return null;
    })
    .filter((field) => field !== null);

  initialValuesCopy.individualDataUpdateFields = [
    ...individualDataArray,
    ...flexFieldsArray,
  ];

  initialValuesCopy.individualDataUpdateFieldsDocuments = camelizeArrayObjects(
    documents,
  );
  initialValuesCopy.individualDataUpdateDocumentsToRemove = camelizeArrayObjects(
    documentsToRemove,
  );
  initialValuesCopy.individualDataUpdateFieldsIdentities = camelizeArrayObjects(
    identities,
  );
  initialValuesCopy.individualDataUpdateIdentitiesToRemove = camelizeArrayObjects(
    identitiesToRemove,
  );
  initialValuesCopy.individualDataUpdateDocumentsToEdit = camelizeArrayObjects(
    documentsToEdit,
  );
  initialValuesCopy.individualDataUpdateIdentitiesToEdit = camelizeArrayObjects(
    identitiesToEdit,
  );
  initialValuesCopy.individualDataUpdateFieldsPaymentChannels = camelizeArrayObjects(
    paymentChannels,
  );
  initialValuesCopy.individualDataUpdatePaymentChannelsToRemove = camelizeArrayObjects(
    paymentChannelsToRemove,
  );
  initialValuesCopy.individualDataUpdatePaymentChannelsToEdit = camelizeArrayObjects(
    paymentChannelsToEdit,
  );

  return initialValuesCopy;
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
    program: ticket.program?.id,
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
    selectedLinkedTickets: ticket.linkedTickets.map(
      (linkedTicket) => linkedTicket.id,
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
        linkedTickets: values.selectedLinkedTickets,
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
        linkedTickets: values.selectedLinkedTickets,
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
        linkedTickets: values.selectedLinkedTickets,
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
        linkedTickets: values.selectedLinkedTickets,
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
        linkedTickets: values.selectedLinkedTickets,
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
        linkedTickets: values.selectedLinkedTickets,
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
        linkedTickets: values.selectedLinkedTickets,
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
        linkedTickets: values.selectedLinkedTickets,
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
        linkedTickets: values.selectedLinkedTickets,
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
        linkedTickets: values.selectedLinkedTickets,
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
  const mapDocumentationToUpdate = (
    documentationToUpdate,
  ): { id: number; name: string; file: File }[] | null => {
    if (documentationToUpdate) {
      return documentationToUpdate
        .filter((el) => el)
        .map((doc) => ({
          id: doc.id,
          name: doc.name,
          file: doc.file,
        }));
    }
    return null;
  };

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
    program: values.program,
    paymentRecord: values.selectedPaymentRecords
      ? values.selectedPaymentRecords[0]
      : null,
    documentation: values.documentation || null,
    documentationToUpdate: mapDocumentationToUpdate(
      values.documentationToUpdate,
    ),
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
