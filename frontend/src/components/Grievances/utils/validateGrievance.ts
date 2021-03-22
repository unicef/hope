import camelCase from 'lodash/camelCase';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../utils/constants';
import { AllAddIndividualFieldsQuery } from '../../../__generated__/graphql';

export function isEmpty(value) {
  console.log('isEmpty', value === undefined || value === null || value === '');
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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const errors: { [id: string]: any } = {};
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
          const { required } = householdFieldsDict[el.fieldName];
          if (el.fieldValue === 0) {
            delete errors.householdDataUpdateFields;
          } else if (!el.fieldName || (isEmpty(el.fieldValue) && required)) {
            errors.householdDataUpdateFields =
              'Field and field value are required';
          }
        });
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) {
      if (!values.selectedIndividual) {
        errors.selectedIndividual = 'Individual is Required';
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
        !values.individualDataUpdateDocumentsToRemove?.length
      ) {
        errors.individualDataUpdateFields =
          'Individual Data Change is Required';
      }
      if (
        values.individualDataUpdateFields?.length &&
        values.individualDataUpdateFields[0]?.fieldName
      ) {
        values.individualDataUpdateFields.forEach((el) => {
          const { required } = individualFieldsDict[el.fieldName];
          if (el.fieldValue === 0) {
            delete errors.individualDataUpdateFields;
          } else if (!el.fieldName || (isEmpty(el.fieldValue) && required)) {
            errors.individualDataUpdateFields =
              'Field and field value are required';
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
