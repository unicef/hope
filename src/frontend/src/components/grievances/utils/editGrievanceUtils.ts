import camelCase from 'lodash/camelCase';
import { GRIEVANCE_CATEGORIES, GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import {
  camelizeArrayObjects,
  thingForSpecificGrievanceType,
} from '@utils/utils';
import { ReactElement } from 'react';
import AddIndividualDataChange from '../AddIndividualDataChange';
import EditHouseholdDataChange from '../EditHouseholdDataChange/EditHouseholdDataChange';
import EditIndividualDataChange from '../EditIndividualDataChange/EditIndividualDataChange';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { PatchedUpdateGrievanceTicket } from '@restgenerated/models/PatchedUpdateGrievanceTicket';
import { UpdateGrievanceTicketExtras } from '@restgenerated/models/UpdateGrievanceTicketExtras';
import { PaymentDetail } from '@restgenerated/models/PaymentDetail';

interface EditValuesTypes {
  priority?: number | string;
  urgency?: number | string;
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
  selectedPaymentRecords: Pick<
    PaymentDetail,
    'id' | 'deliveredQuantity' | 'entitlementQuantity'
  >[];
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
  ticket: GrievanceTicketDetail,
): EditValuesTypes {
  const initialValues = initialValuesArg;
  initialValues.selectedHousehold = ticket.household;
  const individualData = {
    ...ticket.ticketDetails.individualData,
  };
  const flexFields = individualData.flexFields;
  delete individualData.flexFields;
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

interface Field {
  value: string;
}

function mapFieldsToObjects(fields: { [key: string]: Field }) {
  return Object.entries(fields || {})
    .map(([fieldName, field]) =>
      field.value !== undefined ? { fieldName, fieldValue: field.value } : null,
    )
    .filter(Boolean);
}

function prepareInitialValueEditIndividual(initialValues, ticket) {
  const {
    individual,
    individualDataUpdateTicketDetails: { individualData },
  } = ticket;

  const {
    documents,
    documents_to_remove: documentsToRemove,
    documents_to_edit: documentsToEdit,
    identities,
    identities_to_remove: identitiesToRemove,
    identities_to_edit: identitiesToEdit,
    accounts,
    accounts_to_edit: accountsToEdit,
    ...rest
  } = individualData;

  const { flex_fields: flexFields, ...remainingFields } = rest;

  const individualDataArray = mapFieldsToObjects(remainingFields);
  const flexFieldsArray = mapFieldsToObjects(flexFields);

  return {
    ...initialValues,
    selectedIndividual: individual,
    individualDataUpdateFields: [...individualDataArray, ...flexFieldsArray],
    individualDataUpdateFieldsDocuments: camelizeArrayObjects(documents),
    individualDataUpdateDocumentsToRemove:
      camelizeArrayObjects(documentsToRemove),
    individualDataUpdateFieldsIdentities: camelizeArrayObjects(identities),
    individualDataUpdateIdentitiesToRemove:
      camelizeArrayObjects(identitiesToRemove),
    individualDataUpdateDocumentsToEdit: camelizeArrayObjects(documentsToEdit),
    individualDataUpdateIdentitiesToEdit:
      camelizeArrayObjects(identitiesToEdit),
    individualDataUpdateAccountsToEdit: camelizeArrayObjects(
      accountsToEdit,
    ),
    individualDataUpdateFieldsAccounts: camelizeArrayObjects(accounts),
  };
}

function prepareInitialValueEditHousehold(
  initialValuesArg,
  ticket: GrievanceTicketDetail,
): EditValuesTypes {
  const initialValues = initialValuesArg;
  initialValues.selectedHousehold = ticket.household;
  const householdData = {
    ...ticket.ticketDetails.householdData,
  };
  const flexFields = householdData.flexFields;
  delete householdData.flexFields;
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
  ticket: GrievanceTicketDetail,
): EditValuesTypes {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let initialValues: EditValuesTypes = {
    priority: ticket.priority === 0 ? 'Not set' : ticket.priority,
    urgency: ticket.urgency === 0 ? 'Not set' : ticket.urgency,
    partner: ticket.partner?.id,
    comments: ticket.comments || '',
    program: ticket.programs[0]?.id || '',
    description: ticket.description || '',
    assignedTo: ticket?.assignedTo?.id || '',
    category: ticket.category || '',
    language: ticket.language || '',
    admin: ticket.admin2 ? ticket.admin2?.id : null,
    area: ticket.area || '',
    selectedHousehold: ticket.household || null,
    selectedIndividual: ticket.individual || null,
    issueType: ticket.issueType || '',
    paymentRecord: ticket?.paymentRecord?.id || null,
    selectedPaymentRecords: ticket?.paymentRecord?.id
      ? [
          ticket.paymentRecord as Pick<
            PaymentDetail,
            'id' | 'deliveredQuantity' | 'entitlementQuantity'
          >,
        ]
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

export function EmptyComponent(): ReactElement {
  return null;
}
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
function prepareSensitiveVariables(requiredVariables, values) {
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

  // Transform documents and identities to extract value from nested structure
  const transformNestedData = (items) => {
    if (!items || !Array.isArray(items)) return items;
    return items.map((item) => {
      // Handle nested structure {approveStatus, value: {country, key, number}}
      if (item.value && typeof item.value === 'object') {
        return item.value;
      }
      // Handle direct structure {country, key, number} for backward compatibility
      return item;
    });
  };

  return {
    variables: {
      input: {
        ...requiredVariables,
        linkedTickets: values.selectedLinkedTickets,
        extras: {
          individualDataUpdateIssueTypeExtras: {
            individualData: {
              ...individualData,
              documents: transformNestedData(
                values.individualDataUpdateFieldsDocuments,
              ),
              documentsToRemove: values.individualDataUpdateDocumentsToRemove,
              documentsToEdit: transformNestedData(
                values.individualDataUpdateDocumentsToEdit,
              ),
              identities: transformNestedData(
                values.individualDataUpdateFieldsIdentities,
              ),
              identitiesToRemove: values.individualDataUpdateIdentitiesToRemove,
              identitiesToEdit: transformNestedData(
                values.individualDataUpdateIdentitiesToEdit,
              ),
              accountsToEdit:
                values.individualDataUpdateAccountsToEdit,
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
  [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]:
    prepareGrievanceComplaintVariables,
  [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: prepareSensitiveVariables,
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
export function prepareVariables(_businessArea, values, ticket) {
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
    admin: values?.admin,
    area: values.area,
    household: values.selectedHousehold?.id,
    individual: values.selectedIndividual?.id,
    priority:
      values.priority === 'Not set' ||
      values.priority === null ||
      values.priority === ''
        ? 0
        : values.priority,
    urgency:
      values.urgency === 'Not set' ||
      values.urgency === null ||
      values.urgency === ''
        ? 0
        : values.urgency,
    partner: values.partner,
    comments: values.comments,
    program: ticket.programs?.[0]?.id || values?.program,
    paymentRecord: values.selectedPaymentRecords
      ? values.selectedPaymentRecords[0]?.id
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

// REST API version for updating grievance tickets
export function prepareRestUpdateVariables(
  values: EditValuesTypes,
  ticket: GrievanceTicketDetail,
): PatchedUpdateGrievanceTicket {
  const baseUpdate: PatchedUpdateGrievanceTicket = {
    assignedTo: values.assignedTo,
    language: values.language,
    admin: values?.admin,
    area: values.area,
    household: values.selectedHousehold?.id,
    individual: values.selectedIndividual?.id,
    priority:
      values.priority === 'Not set' ||
      values.priority === null ||
      values.priority === ''
        ? 0
        : Number(values.priority),
    urgency:
      values.urgency === 'Not set' ||
      values.urgency === null ||
      values.urgency === ''
        ? 0
        : Number(values.urgency),
    partner: values.partner ? Number(values.partner) : undefined,
    comments: values.comments,
    program: ticket.programs?.[0]?.id || values?.program,
    paymentRecord: values.selectedPaymentRecords
      ? values.selectedPaymentRecords[0]?.id
      : undefined,
    documentation: values.documentation || undefined,
    documentationToUpdate: values.documentationToUpdate
      ? values.documentationToUpdate
          .filter((el) => el)
          .map((doc) => ({
            id: String(doc.id),
            name: doc.name,
            file: doc.file,
          }))
      : undefined,
    documentationToDelete: values.documentationToDelete || undefined,
    linkedTickets: values.selectedLinkedTickets || undefined,
  };

  // For now, keep extras minimal - can be expanded later based on requirements
  if (values.individualData || values.householdDataUpdateFields) {
    const extras: UpdateGrievanceTicketExtras = {};

    // Simple approach for now - just pass the data as-is
    if (values.individualData) {
      extras.individualDataUpdateIssueTypeExtras = {
        individualData: values.individualData,
      };
    }

    if (values.householdDataUpdateFields) {
      extras.householdDataUpdateIssueTypeExtras = {
        householdData: values.householdDataUpdateFields,
      };
    }

    baseUpdate.extras = extras;
  }

  return baseUpdate;
}
