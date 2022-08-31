import camelCase from 'lodash/camelCase';
import {
  GrievanceSteps,
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_SUB_CATEGORIES,
} from '../../../utils/constants';
import { AllAddIndividualFieldsQuery } from '../../../__generated__/graphql';

export function isEmpty(value): boolean {
  return value === undefined || value === null || value === '';
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function validate(
  values,
  allAddIndividualFieldsData: AllAddIndividualFieldsQuery,
  individualFieldsDict,
  householdFieldsDict,
) {
  const category = values.category?.toString();
  const issueType = values.issueType?.toString();
  const errors: { [key: string]: string | { [key: string]: string } } = {};
  if (category === GRIEVANCE_CATEGORIES.DATA_CHANGE) {
    if (issueType === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL) {
      if (!values.selectedHousehold) {
        errors.selectedHousehold = 'Household is Required';
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD) {
      if (!values.selectedHousehold) {
        errors.selectedHousehold = 'Household is Required';
      }
      if (
        //xD
        values.selectedHousehold &&
        !values.householdDataUpdateFields?.[0]?.fieldName
      ) {
        errors.householdDataUpdateFields = 'Household Data Change is Required';
      }
      if (
        values.householdDataUpdateFields?.length &&
        values.householdDataUpdateFields?.[0]?.fieldName
      ) {
        values.householdDataUpdateFields.forEach((el) => {
          if (el?.fieldName) {
            const { required } = householdFieldsDict[el.fieldName];
            if (el.fieldValue === 0) {
              delete errors.householdDataUpdateFields;
            } else if (!el.fieldName || (isEmpty(el.fieldValue) && required)) {
              errors.householdDataUpdateFields =
                'Field and field value are required';
            }
          }
        });
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) {
      if (!values.selectedIndividual) {
        errors.selectedIndividual = 'Individual is Required';
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD) {
      if (!values.selectedHousehold) {
        errors.selectedHousehold = 'Household is Required';
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL) {
      if (!values.selectedIndividual) {
        errors.selectedIndividual = 'Individual is Required';
      }
      if (
        values.selectedIndividual &&
        !values.individualDataUpdateFields[0]?.fieldName &&
        !values.individualDataUpdateFieldsDocuments?.length &&
        !values.individualDataUpdateDocumentsToRemove?.length &&
        !values.individualDataUpdateFieldsIdentities?.length &&
        !values.individualDataUpdateIdentitiesToRemove?.length &&
        !values.individualDataUpdateDocumentsToEdit?.length &&
        !values.individualDataUpdateIdentitiesToEdit?.length &&
        !values.individualDataUpdateFieldsPaymentChannels?.length &&
        !values.individualDataUpdatePaymentChannelsToRemove?.length &&
        !values.individualDataUpdatePaymentChannelsToEdit?.length
      ) {
        errors.individualDataUpdateFields =
          'Individual Data Change is Required';
      }
      if (values.individualDataUpdateFields?.length) {
        values.individualDataUpdateFields.forEach((el) => {
          if (el?.fieldName) {
            if (individualFieldsDict[el.fieldName]) {
              const { required } = individualFieldsDict[el.fieldName];
              if (el.fieldValue === 0) {
                delete errors.individualDataUpdateFields;
              } else if (
                !el.fieldName ||
                (isEmpty(el.fieldValue) && required)
              ) {
                errors.individualDataUpdateFields =
                  'Field and field value are required';
              }
            }
          }
        });
      }

      if (values.individualDataUpdateFieldsDocuments?.length) {
        values.individualDataUpdateFieldsDocuments.forEach((el, index) => {
          const doc = values.individualDataUpdateFieldsDocuments[index];
          if (!doc.country || !doc.type || !doc.number) {
            errors.individualDataUpdateFieldsDocuments =
              'Document country, type and number are required';
          }
        });
      }
      if (values.individualDataUpdateFieldsDocumentsToEdit?.length) {
        values.individualDataUpdateFieldsDocumentsToEdit.forEach(
          (el, index) => {
            const doc = values.individualDataUpdateFieldsDocumentsToEdit[index];
            if (!doc.country || !doc.type || !doc.number) {
              errors.individualDataUpdateFieldsDocumentsToEdit =
                'Document country, type and number are required';
            }
          },
        );
      }
      if (values.individualDataUpdateFieldsIdentities?.length) {
        values.individualDataUpdateFieldsIdentities.forEach((el, index) => {
          const doc = values.individualDataUpdateFieldsIdentities[index];
          if (!doc.country || !doc.agency || !doc.number) {
            errors.individualDataUpdateFieldsIdentities =
              'Identity country, agency and number are required';
          }
        });
      }
      if (values.individualDataUpdateFieldsIdentitiesToEdit?.length) {
        values.individualDataUpdateFieldsIdentitiesToEdit.forEach(
          (el, index) => {
            const doc =
              values.individualDataUpdateFieldsIdentitiesToEdit[index];
            if (!doc.country || !doc.agency || !doc.number) {
              errors.individualDataUpdateFieldsIdentitiesToEdit =
                'Identity country, agency and number are required';
            }
          },
        );
      }
      if (values.individualDataUpdateFieldsPaymentChannelsToEdit?.length) {
        values.individualDataUpdateFieldsPaymentChannelsToEdit.forEach(
          (el, index) => {
            const doc =
              values.individualDataUpdateFieldsPaymentChannelsToEdit[index];
            if (!doc.bankName || !doc.bankAccountNumber) {
              errors.individualDataUpdateFieldsPaymentChannelsToEdit =
                'Bank name and bank account number are required';
            }
          },
        );
      }
      if (values.individualDataUpdateFieldsPaymentChannels?.length) {
        values.individualDataUpdateFieldsPaymentChannels.forEach(
          (el, index) => {
            const doc = values.individualDataUpdateFieldsPaymentChannels[index];
            if (!doc.bankName || !doc.bankAccountNumber) {
              errors.individualDataUpdateFieldsPaymentChannels =
                'Bank name and bank account number are required';
            }
          },
        );
      }
    }
  }
  if (
    category === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
    category === GRIEVANCE_CATEGORIES.DATA_CHANGE
  ) {
    if (!issueType) {
      errors.issueType = 'Issue Type is required';
    }
  }

  if (
    category === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
    issueType === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL
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

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function validateUsingSteps(
  values,
  allAddIndividualFieldsData: AllAddIndividualFieldsQuery,
  individualFieldsDict,
  householdFieldsDict,
  activeStep,
  setValidateData,
) {
  const category = values.category?.toString();
  const issueType = values.issueType?.toString();
  const errors: { [key: string]: string | { [key: string]: string } } = {};
  const verficationStepFields = [
    'size',
    'maleChildrenCount',
    'femaleChildrenCount',
    'childrenDisabledCount',
    'headOfHousehold',
    'countryOrigin',
    'address',
    'village',
    'admin1',
    'unhcrId',
    'months_displaced_h_f',
    'fullName',
    'birthDate',
    'phoneNo',
    'relationship',
  ];
  if (category === GRIEVANCE_CATEGORIES.DATA_CHANGE) {
    if (issueType === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL) {
      if (!values.selectedHousehold && activeStep === GrievanceSteps.Lookup) {
        errors.selectedHousehold = 'Household is Required';
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD) {
      if (!values.selectedHousehold && activeStep === GrievanceSteps.Lookup) {
        errors.selectedHousehold = 'Household is Required';
      }
      if (
        //xD
        values.selectedHousehold &&
        !values.householdDataUpdateFields?.[0]?.fieldName &&
        activeStep === GrievanceSteps.Description
      ) {
        errors.householdDataUpdateFields = 'Household Data Change is Required';
      }
      if (
        values.householdDataUpdateFields?.length &&
        values.householdDataUpdateFields?.[0]?.fieldName
      ) {
        values.householdDataUpdateFields.forEach((el) => {
          if (el?.fieldName) {
            const { required } = householdFieldsDict[el.fieldName];
            if (el.fieldValue === 0) {
              delete errors.householdDataUpdateFields;
            } else if (!el.fieldName || (isEmpty(el.fieldValue) && required)) {
              errors.householdDataUpdateFields =
                'Field and field value are required';
            }
          }
        });
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) {
      if (!values.selectedIndividual && activeStep === GrievanceSteps.Lookup) {
        errors.selectedIndividual = 'Individual is Required';
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD) {
      if (!values.selectedHousehold && activeStep === GrievanceSteps.Lookup) {
        errors.selectedHousehold = 'Household is Required';
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL) {
      if (!values.selectedIndividual && activeStep === GrievanceSteps.Lookup) {
        errors.selectedIndividual = 'Individual is Required';
      }
      if (
        values.selectedIndividual &&
        values.individualDataUpdateFields?.length &&
        !values.individualDataUpdateFields[0]?.fieldName &&
        !values.individualDataUpdateFieldsDocuments?.length &&
        !values.individualDataUpdateDocumentsToRemove?.length &&
        !values.individualDataUpdateFieldsIdentities?.length &&
        !values.individualDataUpdateIdentitiesToRemove?.length &&
        !values.individualDataUpdateDocumentsToEdit?.length &&
        !values.individualDataUpdateIdentitiesToEdit?.length &&
        !values.individualDataUpdateFieldsPaymentChannels?.length &&
        !values.individualDataUpdatePaymentChannelsToRemove?.length &&
        !values.individualDataUpdatePaymentChannelsToEdit?.length &&
        activeStep === GrievanceSteps.Description
      ) {
        errors.individualDataUpdateFields =
          'Individual Data Change is Required';
      }
      if (values.individualDataUpdateFields?.length) {
        values.individualDataUpdateFields.forEach((el) => {
          if (el?.fieldName) {
            if (individualFieldsDict[el.fieldName]) {
              const { required } = individualFieldsDict[el.fieldName];
              if (el.fieldValue === 0) {
                delete errors.individualDataUpdateFields;
              } else if (
                !el.fieldName ||
                (isEmpty(el.fieldValue) && required)
              ) {
                errors.individualDataUpdateFields =
                  'Field and field value are required';
              }
            }
          }
        });
      }

      if (values.individualDataUpdateFieldsDocuments?.length) {
        values.individualDataUpdateFieldsDocuments.forEach((el, index) => {
          const doc = values.individualDataUpdateFieldsDocuments[index];
          if (!doc.country || !doc.type || !doc.number) {
            errors.individualDataUpdateFieldsDocuments =
              'Document country, type and number are required';
          }
        });
      }
      if (values.individualDataUpdateFieldsDocumentsToEdit?.length) {
        values.individualDataUpdateFieldsDocumentsToEdit.forEach(
          (el, index) => {
            const doc = values.individualDataUpdateFieldsDocumentsToEdit[index];
            if (!doc.country || !doc.type || !doc.number) {
              errors.individualDataUpdateFieldsDocumentsToEdit =
                'Document country, type and number are required';
            }
          },
        );
      }
      if (values.individualDataUpdateFieldsIdentities?.length) {
        values.individualDataUpdateFieldsIdentities.forEach((el, index) => {
          const doc = values.individualDataUpdateFieldsIdentities[index];
          if (!doc.country || !doc.agency || !doc.number) {
            errors.individualDataUpdateFieldsIdentities =
              'Identity country, agency and number are required';
          }
        });
      }
      if (values.individualDataUpdateFieldsIdentitiesToEdit?.length) {
        values.individualDataUpdateFieldsIdentitiesToEdit.forEach(
          (el, index) => {
            const doc =
              values.individualDataUpdateFieldsIdentitiesToEdit[index];
            if (!doc.country || !doc.agency || !doc.number) {
              errors.individualDataUpdateFieldsIdentitiesToEdit =
                'Identity country, agency and number are required';
            }
          },
        );
      }
      if (values.individualDataUpdateFieldsPaymentChannelsToEdit?.length) {
        values.individualDataUpdateFieldsPaymentChannelsToEdit.forEach(
          (el, index) => {
            const doc =
              values.individualDataUpdateFieldsPaymentChannelsToEdit[index];
            if (!doc.bankName || !doc.bankAccountNumber) {
              errors.individualDataUpdateFieldsPaymentChannelsToEdit =
                'Bank name and bank account number are required';
            }
          },
        );
      }
      if (values.individualDataUpdateFieldsPaymentChannels?.length) {
        values.individualDataUpdateFieldsPaymentChannels.forEach(
          (el, index) => {
            const doc = values.individualDataUpdateFieldsPaymentChannels[index];
            if (!doc.bankName || !doc.bankAccountNumber) {
              errors.individualDataUpdateFieldsPaymentChannels =
                'Bank name and bank account number are required';
            }
          },
        );
      }
    }
  }
  if (
    category === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
    category === GRIEVANCE_CATEGORIES.DATA_CHANGE
  ) {
    if (!issueType) {
      errors.issueType = 'Issue Type is required';
    }
  }

  if (
    category === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
    issueType === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL &&
    activeStep === GrievanceSteps.Description
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
  const householdRequiredGrievanceTypes = [
    GRIEVANCE_SUB_CATEGORIES.PAYMENT_COMPLAINT,
    GRIEVANCE_SUB_CATEGORIES.FSP_COMPLAINT,
  ];
  if (
    activeStep === GrievanceSteps.Lookup &&
    !values.selectedHousehold &&
    householdRequiredGrievanceTypes.includes(values.subCategory)
  ) {
    errors.selectedHousehold = 'Household is Required';
  }
  if (activeStep === GrievanceSteps.Lookup) {
    const individualRequiredIssueTypes = [
      GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL,
      GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL,
    ];
    const householdRequiredIssueTypes = [
      GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD,
      GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD,
    ];
    const isHouseholdRequired = householdRequiredIssueTypes.includes(
      values.issueType,
    );
    const isIndividualRequired = individualRequiredIssueTypes.includes(
      values.issueType,
    );
    if (isIndividualRequired && !values.selectedIndividual) {
      errors.selectedIndividual = 'Individual is Required';
    } else if (isHouseholdRequired && !values.selectedHousehold) {
      errors.selectedHousehold = 'Household is Required';
    }
  }
  if (
    activeStep === GrievanceSteps.Verification &&
    (values.selectedHousehold ||
      (values.selectedIndividual && !values.verificationRequired))
  ) {
    if (
      verficationStepFields.filter((item) => values[item] === true).length < 5
    ) {
      setValidateData(true);
      errors.verificationRequired = 'Select correctly minimum 5 questions';
    }
  }
  if (activeStep === GrievanceSteps.Description) {
    setValidateData(true);
  }
  return errors;
}
