import camelCase from 'lodash/camelCase';
import React from 'react';
import * as Yup from 'yup';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../utils/constants';
import { thingForSpecificGrievanceType } from '../../../utils/utils';
import {
  AllAddIndividualFieldsQuery,
  GrievanceTicketQuery,
} from '../../../__generated__/graphql';
import { AddIndividualDataChange } from '../AddIndividualDataChange';
import { EditIndividualDataChange } from '../EditIndividualDataChange';
import { EditHouseholdDataChange } from '../EditHouseholdDataChange';

function prepareInitialValueAddIndividual(
  initialValuesArg,
  ticket: GrievanceTicketQuery['grievanceTicket'],
) {
  const initialValues = initialValuesArg;
  initialValues.selectedHousehold = ticket.household;
  const individualData = {
    ...ticket.addIndividualTicketDetails.individualData,
  };
  initialValues.individualData = Object.entries(individualData).reduce(
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
) {
  const initialValues = initialValuesArg;
  initialValues.selectedIndividual = ticket.individual;
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  const documents = individualData?.documents;
  const documentsToRemove = individualData.documents_to_remove;
  delete individualData.documents;
  delete individualData.documents_to_remove;
  delete individualData.previous_documents;
  initialValues.individualDataUpdateFields = Object.entries(individualData).map(
    (entry: [string, { value: string }]) => ({
      fieldName: entry[0],
      fieldValue: entry[1].value,
    }),
  );
  initialValues.individualDataUpdateFieldsDocuments = documents.map(
    (item) => item.value,
  );
  initialValues.individualDataUpdateDocumentsToRemove = documentsToRemove.map(
    (item) => item.value,
  );
  return initialValues;
}
function prepareInitialValueEditHousehold(
  initialValuesArg,
  ticket: GrievanceTicketQuery['grievanceTicket'],
) {
  const initialValues = initialValuesArg;
  initialValues.selectedHousehold = ticket.household;
  const householdData = {
    ...ticket.householdDataUpdateTicketDetails.householdData,
  };
  initialValues.householdDataUpdateFields = Object.entries(householdData).map(
    (entry: [string, { value: string }]) => ({
      fieldName: entry[0],
      fieldValue: entry[1].value,
    }),
  );
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
) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let initialValues: { [id: string]: any } = {
    description: ticket.description || '',
    assignedTo: ticket.assignedTo.id || '',
    category: ticket.category || null,
    language: ticket.language || '',
    consent: ticket.consent || false,
    admin: ticket.admin || '',
    area: ticket.area || '',
    selectedHousehold: ticket.household || null,
    selectedIndividual: ticket.individual || null,
    identityVerified: false,
    issueType: ticket.issueType || null,
    selectedPaymentRecords: ticket?.paymentRecord?.id
      ? [ticket.paymentRecord.id]
      : [],
    selectedRelatedTickets: ticket.relatedTickets.map(
      (relatedTicket) => relatedTicket.id,
    ),
  };
  const prepareInitialValueFunction = thingForSpecificGrievanceType(
    ticket,
    prepareInitialValueDict,
    (initialValue) => initialValue,
  );
  initialValues = prepareInitialValueFunction(initialValues, ticket);
  return initialValues;
}
export const validationSchema = Yup.object().shape({
  description: Yup.string().required('Description is required'),
  assignedTo: Yup.string().required('Assigned To is required'),
  category: Yup.string()
    .required('Category is required')
    .nullable(),
  admin: Yup.string(),
  area: Yup.string(),
  language: Yup.string().required('Language is required'),
  consent: Yup.bool().oneOf([true], 'Consent is required'),
  selectedPaymentRecords: Yup.array()
    .of(Yup.string())
    .nullable(),
  selectedRelatedTickets: Yup.array()
    .of(Yup.string())
    .nullable(),
});
export const EmptyComponent = (): React.ReactElement => null;
export const dataChangeComponentDict = {
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: {
    [GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL]: AddIndividualDataChange,
    [GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL]: EditIndividualDataChange,
    [GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD]: EditHouseholdDataChange,
  },
};

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareFeedbackVariables(requiredVariables, values) {
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
function prepareGrievanceComplaintVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          category: {
            grievanceComplaintTicketExtras: {
              household: values.selectedHousehold?.id,
              individual: values.selectedIndividual?.id,
              paymentRecord: values.selectedPaymentRecords,
            },
          },
        },
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
        extras: {
          category: {
            sensitiveGrievanceTicketExtras: {
              household: values.selectedHousehold?.id,
              individual: values.selectedIndividual?.id,
              paymentRecord: values.selectedPaymentRecords,
            },
          },
        },
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareAddIndividualVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          addIndividualIssueTypeExtras: {
            individualData: values.individualData,
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
        extras: {
          issueType: {
            individualDeleteIssueTypeExtras: {
              individual: values.selectedIndividual?.id,
            },
          },
        },
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareEditIndividualVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          issueType: {
            individualDataUpdateIssueTypeExtras: {
              individual: values.selectedIndividual?.id,
              individualData: {
                ...values.individualDataUpdateFields
                  .filter((item) => item.fieldName)
                  .reduce((prev, current) => {
                    // eslint-disable-next-line no-param-reassign
                    prev[camelCase(current.fieldName)] = current.fieldValue;
                    return prev;
                  }, {}),
                documents: values.individualDataUpdateFieldsDocuments,
                documentsToRemove: values.individualDataUpdateDocumentsToRemove,
              },
            },
          },
        },
      },
    },
  };
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareEditHouseholdVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedRelatedTickets,
        extras: {
          issueType: {
            householdDataUpdateIssueTypeExtras: {
              household: values.selectedHousehold?.id,
              householdData: values.householdDataUpdateFields
                .filter((item) => item.fieldName)
                .reduce((prev, current) => {
                  // eslint-disable-next-line no-param-reassign
                  prev[camelCase(current.fieldName)] = current.fieldValue;
                  return prev;
                }, {}),
            },
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
  [GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK]: prepareFeedbackVariables,
  [GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK]: prepareFeedbackVariables,
  [GRIEVANCE_CATEGORIES.REFERRAL]: prepareFeedbackVariables,
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
    admin: values.admin,
    area: values.area,
  };
  const prepareFunction = thingForSpecificGrievanceType(
    values,
    prepareVariablesDict,
    prepareDefaultVariables,
    grievanceTypeIssueTypeDict,
  );
  return prepareFunction(requiredVariables, values);
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function validate(
  values,
  allAddIndividualFieldsData: AllAddIndividualFieldsQuery,
) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const errors: { [id: string]: any } = {};
  if (
    values.category === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
    values.issueType === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL
  ) {
    const individualDataErrors = {};
    const individualData = values.individualData || {};
    for (const field of allAddIndividualFieldsData.allAddIndividualsFieldsAttributes) {
      const fieldName = camelCase(field.name);
      if (
        field.required &&
        (individualData[fieldName] === null ||
          individualData[fieldName] === undefined)
      ) {
        individualDataErrors[fieldName] = 'Field Required';
      }
      if (Object.keys(individualDataErrors).length > 0) {
        errors.individualData = individualDataErrors;
      }
    }
  }
  return errors;
}
