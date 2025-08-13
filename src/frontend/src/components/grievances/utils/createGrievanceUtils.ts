import { CreateGrievanceTicket } from '@restgenerated/models/CreateGrievanceTicket';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_ISSUE_TYPES_NAMES,
} from '@utils/constants';
import { thingForSpecificGrievanceType } from '@utils/utils';
import camelCase from 'lodash/camelCase';
import { removeIdPropertyFromObjects } from './helpers';
import { CategoryB41Enum } from '@restgenerated/models/CategoryB41Enum';

export const replaceLabels = (text, _beneficiaryGroup) => {
  if (!_beneficiaryGroup || !text) {
    return '';
  }
  if (!_beneficiaryGroup) {
    return text;
  }
  return text
    .replace(/Individual/g, _beneficiaryGroup.memberLabel)
    .replace(/Household/g, _beneficiaryGroup.groupLabel);
};

export function isShowIssueType(category: string | CategoryB41Enum): boolean {
  const cat = category?.toString();
  return (
    cat === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
    cat === GRIEVANCE_CATEGORIES.DATA_CHANGE ||
    cat === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION ||
    cat === GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT
  );
}
export const getIssueTypeToDisplay = (issueType: number): string =>
  (issueType &&
    GRIEVANCE_ISSUE_TYPES_NAMES[issueType]
      ?.toLowerCase()
      ?.replace(/_/g, ' ')
      ?.replace(/\b\w/g, (char) => char.toUpperCase())) ||
  '';

export const selectedIssueType = (formValues, issueTypeDict): string => {
  const subCategoriesObj =
    issueTypeDict[formValues.category]?.subCategories || [];

  const subcategories = Object.entries(subCategoriesObj).map(
    ([value, name]) => ({
      name,
      value,
    }),
  );
  const issueType = formValues.issueType.toString();
  return (
    (
      subcategories.find((el) => el.value === issueType) as
        | { name: string; value: string }
        | undefined
    )?.name || '-'
  );
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
        issueType: parseInt(values.issueType, 10),
        linkedTickets: values.selectedLinkedTickets,
        extras: {
          category: {
            grievanceComplaintTicketExtras: {
              household: values.selectedHousehold?.id,
              individual: values.selectedIndividual?.id,
              paymentRecord:
                values.selectedPaymentRecords?.map((el) => el.id) || null,
            },
          },
        },
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
        issueType: parseInt(values.issueType, 10),
        partner: parseInt(values.partner, 10),
        linkedTickets: values.selectedLinkedTickets,
        extras: {
          category: {
            sensitiveGrievanceTicketExtras: {
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

  const newlyAddedDocumentsWithoutIds = removeIdPropertyFromObjects(
    values.individualData.documents,
  );

  const newlyAddedIdentitiesWithoutIds = removeIdPropertyFromObjects(
    values.individualData.identities,
  );

  return {
    variables: {
      input: {
        ...requiredVariables,
        issueType: parseInt(values.issueType, 10),
        linkedTickets: values.selectedLinkedTickets,
        extras: {
          issueType: {
            addIndividualIssueTypeExtras: {
              household: values.selectedHousehold?.id,
              individualData: {
                ...values.individualData,
                documents: newlyAddedDocumentsWithoutIds,
                identities: newlyAddedIdentitiesWithoutIds,
                flexFields,
              },
            },
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
        issueType: parseInt(values.issueType, 10),
        linkedTickets: values.selectedLinkedTickets,
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

export function customSnakeCase(str: string): string {
  return (
    str
      // Insert _ between lowercase and uppercase
      .replace(/([a-z])([A-Z])/g, '$1_$2')
      // Insert _ between letter and number
      .replace(/([a-zA-Z])([0-9])/g, '$1_$2')
      // Insert _ between number and letter
      .replace(/([0-9])([a-zA-Z])/g, '$1_$2')
      // Replace age group numbers like 05, 611, 1217, 1859, 60 with correct underscores
      .replace(/_0(\d)(_|$)/g, '_0_$1$2') // 05 -> 0_5
      .replace(/_6(\d{2})(_|$)/g, '_6_$1$2') // 611 -> 6_11
      .replace(/_1(\d{2})(_|$)/g, '_1_$1$2') // 1217, 1859 -> 12_17, 18_59
      .replace(/_6_0(_|$)/g, '_60$1') // 60 stays as 60 (optional, if you want _60 not _6_0)
      .toLowerCase()
  );
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareDeleteHouseholdVariables(requiredVariables, values) {
  return {
    variables: {
      input: {
        ...requiredVariables,
        issueType: parseInt(values.issueType, 10),
        linkedTickets: values.selectedLinkedTickets,
        extras: {
          issueType: {
            householdDeleteIssueTypeExtras: {
              household: values.selectedHousehold?.id,
            },
          },
        },
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

  const newlyAddedDocumentsWithoutIds = removeIdPropertyFromObjects(
    values.individualDataUpdateFieldsDocuments,
  );

  const newlyAddedIdentitiesWithoutIds = removeIdPropertyFromObjects(
    values.individualDataUpdateFieldsIdentities,
  );

  const newlyAddedAccountsWithoutIds = removeIdPropertyFromObjects(
    values.individualDataUpdateFieldsAccounts,
  )?.map((account) => {
    const { name, ...dataFields } = account;
    const { dynamicFields, ...restDataFields } = dataFields;
    const mappedDynamicFields = dynamicFields?.reduce((acc, curr) => {
      if (curr.key) acc[curr.key] = curr.value;
      return acc;
    }, {});

    return {
      name,
      dataFields: {
        ...restDataFields,
        ...mappedDynamicFields,
      },
    };
  });

  const accountsToEdit = values.individualDataUpdateAccountsToEdit?.map(
    (account) => {
      const { id, name, ...dataFields } = account;
      const { dynamicFields, ...restDataFields } = dataFields;
      const mappedDynamicFields = dynamicFields?.reduce((acc, curr) => {
        if (curr.key) acc[curr.key] = curr.value;
        return acc;
      }, {});
      return {
        id,
        name,
        dataFields: {
          ...restDataFields,
          ...mappedDynamicFields,
        },
      };
    },
  );

  return {
    variables: {
      input: {
        ...requiredVariables,
        issueType: parseInt(values.issueType, 10),
        linkedTickets: values.selectedLinkedTickets,
        extras: {
          issueType: {
            individualDataUpdateIssueTypeExtras: {
              individual: values.selectedIndividual?.id,
              individualData: {
                ...individualData,
                documents: newlyAddedDocumentsWithoutIds,
                documentsToRemove: values.individualDataUpdateDocumentsToRemove,
                documentsToEdit: values.individualDataUpdateDocumentsToEdit,
                identities: newlyAddedIdentitiesWithoutIds,
                identitiesToRemove:
                  values.individualDataUpdateIdentitiesToRemove,
                identitiesToEdit: values.individualDataUpdateIdentitiesToEdit,
                accounts: newlyAddedAccountsWithoutIds,
                accountsToEdit: accountsToEdit,
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
  const householdDataUpdateIssueTypeExtras = {
    household: values.selectedHousehold?.id,
    householdData: { ...householdData, flexFields },
  } as {
    household: any;
    householdData: any;
    roles?: any;
  };
  console.log('values.roles', values.roles);
  if (Array.isArray(values.roles) && values.roles.length > 0) {
    householdDataUpdateIssueTypeExtras.householdData.roles = values.roles;
  }
  return {
    variables: {
      input: {
        ...requiredVariables,
        issueType: parseInt(values.issueType, 10),
        linkedTickets: values.selectedLinkedTickets,
        extras: {
          issueType: {
            householdDataUpdateIssueTypeExtras,
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
    [GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD]: prepareDeleteHouseholdVariables,
    [GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL]: prepareEditIndividualVariables,
    [GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD]: prepareEditHouseholdVariables,
  },
};
const grievanceTypeIssueTypeDict = {
  [GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK]: false,
  [GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK]: false,
  [GRIEVANCE_CATEGORIES.REFERRAL]: false,
  [GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT]: 'IGNORE',
  [GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE]: 'IGNORE',
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: true,
};
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function prepareVariables(businessArea, values) {
  const requiredVariables = {
    businessArea,
    description: values.description,
    assignedTo: values.assignedTo,
    category: parseInt(values.category, 10),
    consent: values.consent,
    language: values.language,
    admin: values.admin,
    area: values.area,
    priority:
      values.priority === 'Not set' || values.priority === null
        ? 0
        : values.priority,
    urgency:
      values.urgency === 'Not set' || values.urgency === null
        ? 0
        : values.urgency,
    partner: values.partner,
    comments: values.comments,
    program: values.program,
    linkedFeedbackId: values.linkedFeedbackId,
    documentation: values.documentation,
  };
  const prepareFunction = thingForSpecificGrievanceType(
    values,
    prepareVariablesDict,
    prepareDefaultVariables,
    grievanceTypeIssueTypeDict,
  );
  return prepareFunction(requiredVariables, values);
}

// Transform form values to REST API CreateGrievanceTicket format
export function prepareRestVariables(
  businessArea: string,
  values: any,
): CreateGrievanceTicket {
  // Build extras based on category and issue type
  const extras: any = {};
  const category = parseInt(values.category, 10);
  const issueType = values.issueType
    ? parseInt(values.issueType, 10)
    : undefined;

  // Category-specific extras
  if (category === parseInt(GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK, 10)) {
    extras.category = {
      positiveFeedbackTicketExtras: {
        household: values.selectedHousehold?.id,
        individual: values.selectedIndividual?.id,
      },
    };
  } else if (
    category === parseInt(GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK, 10)
  ) {
    extras.category = {
      negativeFeedbackTicketExtras: {
        household: values.selectedHousehold?.id,
        individual: values.selectedIndividual?.id,
      },
    };
  } else if (category === parseInt(GRIEVANCE_CATEGORIES.REFERRAL, 10)) {
    extras.category = {
      referralTicketExtras: {
        household: values.selectedHousehold?.id,
        individual: values.selectedIndividual?.id,
      },
    };
  } else if (
    category === parseInt(GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT, 10)
  ) {
    extras.category = {
      grievanceComplaintTicketExtras: {
        household: values.selectedHousehold?.id,
        individual: values.selectedIndividual?.id,
        paymentRecord:
          values.selectedPaymentRecords?.map((el) => el.id) || null,
      },
    };
  } else if (
    category === parseInt(GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE, 10)
  ) {
    extras.category = {
      sensitiveGrievanceTicketExtras: {
        household: values.selectedHousehold?.id,
        individual: values.selectedIndividual?.id,
        paymentRecord:
          values.selectedPaymentRecords?.map((el) => el.id) || null,
      },
    };
  }

  // Issue type-specific extras for DATA_CHANGE category
  if (
    category === parseInt(GRIEVANCE_CATEGORIES.DATA_CHANGE, 10) &&
    issueType
  ) {
    if (issueType === parseInt(GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL, 10)) {
      let { flexFields } = values.individualData;
      if (flexFields) {
        flexFields = { ...flexFields };
        for (const [key, value] of Object.entries(flexFields)) {
          if (value === '') {
            delete flexFields[key];
          }
        }
      }

      const newlyAddedDocumentsWithoutIds = removeIdPropertyFromObjects(
        values.individualData.documents,
      );
      const newlyAddedIdentitiesWithoutIds = removeIdPropertyFromObjects(
        values.individualData.identities,
      );

      extras.issueType = {
        addIndividualIssueTypeExtras: {
          household: values.selectedHousehold?.id,
          individualData: {
            ...values.individualData,
            documents: newlyAddedDocumentsWithoutIds,
            identities: newlyAddedIdentitiesWithoutIds,
            flexFields,
          },
        },
      };
    } else if (
      issueType === parseInt(GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL, 10)
    ) {
      extras.issueType = {
        individualDeleteIssueTypeExtras: {
          individual: values.selectedIndividual?.id,
        },
      };
    } else if (
      issueType === parseInt(GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD, 10)
    ) {
      extras.issueType = {
        householdDeleteIssueTypeExtras: {
          household: values.selectedHousehold?.id,
        },
      };
    } else if (
      issueType === parseInt(GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL, 10)
    ) {
      const individualData = values.individualDataUpdateFields
        .filter((item) => item.fieldName && !item.isFlexField)
        .reduce((prev, current) => {
          prev[camelCase(current.fieldName)] = current.fieldValue;
          return prev;
        }, {});

      const flexFields = values.individualDataUpdateFields
        .filter((item) => item.fieldName && item.isFlexField)
        .reduce((prev, current) => {
          prev[camelCase(current.fieldName)] = current.fieldValue;
          return prev;
        }, {});
      individualData.flexFields = flexFields;

      const newlyAddedDocumentsWithoutIds = removeIdPropertyFromObjects(
        values.individualDataUpdateFieldsDocuments,
      );
      const newlyAddedIdentitiesWithoutIds = removeIdPropertyFromObjects(
        values.individualDataUpdateFieldsIdentities,
      );
      const newlyAddedPaymentChannelsWithoutIds = removeIdPropertyFromObjects(
        values.individualDataUpdateFieldsPaymentChannels,
      );

      extras.issueType = {
        individualDataUpdateIssueTypeExtras: {
          individual: values.selectedIndividual?.id,
          individualData: {
            ...individualData,
            documents: newlyAddedDocumentsWithoutIds,
            documentsToRemove: values.individualDataUpdateDocumentsToRemove,
            documentsToEdit: values.individualDataUpdateDocumentsToEdit,
            identities: newlyAddedIdentitiesWithoutIds,
            identitiesToRemove: values.individualDataUpdateIdentitiesToRemove,
            identitiesToEdit: values.individualDataUpdateIdentitiesToEdit,
            paymentChannels: newlyAddedPaymentChannelsWithoutIds,
            paymentChannelsToRemove:
              values.individualDataUpdatePaymentChannelsToRemove,
            paymentChannelsToEdit:
              values.individualDataUpdatePaymentChannelsToEdit,
          },
        },
      };
    } else if (
      issueType === parseInt(GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD, 10)
    ) {
      const householdData = values.householdDataUpdateFields
        .filter((item) => item.fieldName && !item.isFlexField)
        .reduce((prev, current) => {
          prev[current.fieldName] = current.fieldValue;
          return prev;
        }, {});
      const flexFields = values.householdDataUpdateFields
        .filter((item) => item.fieldName && item.isFlexField)
        .reduce((prev, current) => {
          prev[current.fieldName] = current.fieldValue;
          return prev;
        }, {});

      extras.issueType = {
        householdDataUpdateIssueTypeExtras: {
          household: values.selectedHousehold?.id,
          householdData: { ...householdData, flexFields },
        },
      };
    }
  }

  return {
    description: values.description,
    assignedTo: values.assignedTo,
    category,
    issueType,
    admin: values.admin,
    area: values.area,
    language: values.language,
    consent: values.consent,
    linkedTickets: values.selectedLinkedTickets || [],
    extras: Object.keys(extras).length > 0 ? extras : {},
    priority:
      values.priority === 'Not set' || values.priority === null
        ? 0
        : values.priority,
    urgency:
      values.urgency === 'Not set' || values.urgency === null
        ? 0
        : values.urgency,
    partner: values.partner ? parseInt(values.partner, 10) : undefined,
    program: values.program,
    comments: values.comments,
    linkedFeedbackId: values.linkedFeedbackId,
    documentation: values.documentation || [],
  };
}

export const matchGrievanceUrlByCategory = (category: number): string => {
  if (!category) return null;
  const categoryString = category.toString();
  const systemGeneratedGrievanceCategories = [
    GRIEVANCE_CATEGORIES.PAYMENT_VERIFICATION,
    GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION,
    GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING,
  ];
  if (systemGeneratedGrievanceCategories.includes(categoryString)) {
    return 'system-generated';
  }
  return 'user-generated';
};

export const getGrievanceDetailsPath = (
  ticketId: string,
  category: number,
  baseUrl: string,
): string => {
  if (!ticketId || !category) {
    return null;
  }
  return `/${baseUrl}/grievance/tickets/${matchGrievanceUrlByCategory(
    category,
  )}/${ticketId}`;
};

export const getGrievanceEditPath = (
  ticketId: string,
  category: number,
  baseUrl: string,
): string => {
  if (!ticketId || !category) {
    return null;
  }
  return `/${baseUrl}/grievance/edit-ticket/${matchGrievanceUrlByCategory(
    category,
  )}/${ticketId}`;
};

export const categoriesAndColors = [
  { category: 'Data Change', color: '#FFAA20' },
  { category: 'Grievance Complaint', color: '#023E90' },
  { category: 'Needs Adjudication', color: '#05C9B7' },
  { category: 'Negative Feedback', color: '#FF0200' },
  { category: 'Payment Verification', color: '#FFE399' },
  { category: 'Positive Feedback', color: '#13CB17' },
  { category: 'Referral', color: '#FFAA20' },
  { category: 'Sensitive Grievance', color: '#7FCB28' },
  { category: 'System Flagging', color: '#00867B' },
];

/**
 * Converts a nested object into FormData, recursively flattening keys using bracket notation and snake_case.
 * - Files are appended directly.
 * - Booleans are serialized as 'true'/'false'.
 * - Arrays: Non-empty arrays are expanded with indexed keys; empty arrays are omitted (not sent).
 * - Objects: Empty objects are always sent as '{}'.
 * - All keys are snake_cased and use bracket notation for nesting.
 *
 * This utility is robust to OpenAPI codegen overwrites and backend requirements.
 *
 * Example:
 *   { fooBar: [ { nestedKey: true } ], emptyArr: [], emptyObj: {} }
 *   =>
 *   foo_bar[0][nested_key]=true
 *   empty_obj={}
 *   (empty_arr is omitted)
 */

export function grievanceRequestToFormData(
  obj: any,
  form?: FormData,
  parentKey?: string,
): FormData {
  const formData = form || new FormData();
  for (const key in obj) {
    if (obj[key] === undefined || obj[key] === null) continue;
    const value = obj[key];
    const snakeKey = customSnakeCase(key);
    let formKey;
    if (Array.isArray(obj)) {
      // Array: use bracket notation for index
      formKey = parentKey ? `${parentKey}[${key}]` : key;
    } else {
      // Object: use dot notation for nesting
      formKey = parentKey ? `${parentKey}.${snakeKey}` : snakeKey;
    }

    if (value instanceof File) {
      formData.append(formKey, value);
    } else if (Array.isArray(value)) {
      if (value.length === 0) {
        continue;
      } else {
        value.forEach((item, idx) => {
          grievanceRequestToFormData(item, formData, `${formKey}[${idx}]`);
        });
      }
    } else if (typeof value === 'object' && value !== null) {
      if (Object.keys(value).length === 0) {
        // Do not send empty objects at all
        continue;
      } else {
        grievanceRequestToFormData(value, formData, formKey);
      }
    } else if (typeof value === 'boolean') {
      formData.append(formKey, value ? 'true' : 'false');
    } else {
      formData.append(formKey, value);
    }
  }
  return formData;
}
