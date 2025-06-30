import camelCase from 'lodash/camelCase';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GrievanceSteps,
} from '@utils/constants';

export function isEmpty(value): boolean {
  return value === undefined || value === null || value === '';
}

// TODO MB ADD NEEDS ADJ TICKETS REQUIRED CATEGORY

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function validate(
  values,
  addIndividualFieldsData: Array<any> | null,
  individualFieldsDict,
  householdFieldsDict,
  beneficiaryGroup,
) {
  const category = values.category?.toString();
  const issueType = values.issueType?.toString();
  const errors: { [key: string]: string | { [key: string]: string } } = {};
  if (category === GRIEVANCE_CATEGORIES.DATA_CHANGE) {
    if (issueType === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL) {
      if (!values.selectedHousehold) {
        errors.selectedHousehold = `${beneficiaryGroup?.groupLabel} is Required`;
      }
      if (values.individualData?.documents?.length) {
        values.individualData.documents
          .filter((el) => el)
          .forEach((doc) => {
            // Handle nested structure: doc.value.{country, key, number} or direct structure
            const docValue = doc.value || doc;
            if (!docValue.country || !docValue.key || !docValue.number) {
              errors.individualData =
                'Document type, country and number are required';
            }
          });
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD) {
      if (!values.selectedHousehold) {
        errors.selectedHousehold = `${beneficiaryGroup?.groupLabel} is Required`;
      }
      if (
        // xD
        values.selectedHousehold &&
        !values.householdDataUpdateFields?.[0]?.fieldName
      ) {
        errors.householdDataUpdateFields = `${beneficiaryGroup?.groupLabel} Data Change is Required`;
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
        errors.selectedIndividual = `${beneficiaryGroup?.memberLabel} is Required`;
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD) {
      if (!values.selectedHousehold) {
        errors.selectedHousehold = `${beneficiaryGroup?.groupLabel} is Required`;
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL) {
      if (!values.selectedIndividual) {
        errors.selectedIndividual = `${beneficiaryGroup?.memberLabel} is Required`;
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
        !values.individualDataUpdatePaymentChannelsToEdit?.length &&
        !values.individualDataUpdateDeliveryMechanismDataToEdit?.length
      ) {
        errors.individualDataUpdateFields = `${beneficiaryGroup?.memberLabel} Data Change is Required`;
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
        values.individualDataUpdateFieldsDocuments
          .filter((el) => el)
          .forEach((doc) => {
            // Handle nested structure: doc.value.{country, key, number}
            const docValue = doc.value || doc;
            if (!docValue.country || !docValue.key || !docValue.number) {
              errors.individualDataUpdateFieldsDocuments =
                'Document type, country and number are required';
            }
          });
      }
      if (values.individualDataUpdateFieldsDocumentsToEdit?.length) {
        values.individualDataUpdateFieldsDocumentsToEdit
          .filter((el) => el)
          .forEach((doc) => {
            // Handle nested structure: doc.value.{country, key, number}
            const docValue = doc.value || doc;
            if (!docValue.country || !docValue.key || !docValue.number) {
              errors.individualDataUpdateFieldsDocumentsToEdit =
                'Document type, country and number are required';
            }
          });
      }
      if (values.individualDataUpdateFieldsIdentities?.length) {
        values.individualDataUpdateFieldsIdentities
          .filter((el) => el)
          .forEach((doc) => {
            // Handle nested structure: doc.value.{country, partner, number}
            const docValue = doc.value || doc;
            const partner = docValue.partner || docValue.agency; // For backward compatibility
            if (!docValue.country || !partner || !docValue.number) {
              errors.individualDataUpdateFieldsIdentities =
                'Identity partner, country and number are required';
            }
          });
      }
      if (values.individualDataUpdateFieldsIdentitiesToEdit?.length) {
        values.individualDataUpdateFieldsIdentitiesToEdit
          .filter((el) => el)
          .forEach((doc) => {
            // Handle nested structure: doc.value.{country, partner, number}
            const docValue = doc.value || doc;
            const partner = docValue.partner || docValue.agency; // For backward compatibility
            if (!docValue.country || !partner || !docValue.number) {
              errors.individualDataUpdateFieldsIdentitiesToEdit =
                'Identity partner, country and number are required';
            }
          });
      }
      if (values.individualDataUpdateFieldsPaymentChannelsToEdit?.length) {
        values.individualDataUpdateFieldsPaymentChannelsToEdit
          .filter((el) => el)
          .forEach((doc) => {
            if (!doc.bankName || !doc.bankAccountNumber) {
              errors.individualDataUpdateFieldsPaymentChannelsToEdit =
                'Bank name and bank account number are required';
            }
          });
      }
      if (values.individualDataUpdateFieldsPaymentChannels?.length) {
        values.individualDataUpdateFieldsPaymentChannels
          .filter((el) => el)
          .forEach((doc) => {
            if (!doc.bankName || !doc.bankAccountNumber) {
              errors.individualDataUpdateFieldsPaymentChannels =
                'Bank name and bank account number are required';
            }
          });
      }
    }
  }
  if (
    category === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
    category === GRIEVANCE_CATEGORIES.DATA_CHANGE ||
    category === GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT ||
    category === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION
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
    if (addIndividualFieldsData) {
      for (const field of addIndividualFieldsData) {
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
  }

  if (values.documentation?.length) {
    values.documentation
      .filter((el) => el)
      .forEach((doc) => {
        if (!doc.name || !doc.file) {
          errors.documentation =
            'Grievance Supporting Document name and file are required';
        }
      });
  }
  if (values.documentationToUpdate?.length) {
    values.documentationToUpdate
      .filter((el) => el)
      .forEach((doc) => {
        if (!doc.name || !doc.file) {
          errors.documentationToUpdate =
            'Grievance Supporting Document name and file are required';
        }
      });
  }
  return errors;
}

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function validateUsingSteps(
  values,
  addIndividualFieldsData: Array<any> | null,
  individualFieldsDict,
  householdFieldsDict,
  activeStep,
  setValidateData,
  beneficiaryGroup,
) {
  const category = values.category?.toString();
  const issueType = values.issueType?.toString();
  const errors: { [key: string]: string | { [key: string]: string } } = {};

  // TODO: enable this when questionnaire verification is required
  // const verficationStepFields = [
  //   'size',
  //   'maleChildrenCount',
  //   'femaleChildrenCount',
  //   'childrenDisabledCount',
  //   'headOfHousehold',
  //   'countryOrigin',
  //   'address',
  //   'village',
  //   'admin1',
  //   'admin2',
  //   'admin3',
  //   'unhcrId',
  //   'months_displaced_h_f',
  //   'fullName',
  //   'birthDate',
  //   'phoneNo',
  //   'relationship',
  //   'sex',
  // ];

  if (category === GRIEVANCE_CATEGORIES.DATA_CHANGE) {
    if (issueType === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL) {
      if (!values.selectedHousehold && activeStep === GrievanceSteps.Lookup) {
        errors.selectedHousehold = `${beneficiaryGroup?.groupLabel} is Required`;
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD) {
      if (!values.selectedHousehold && activeStep === GrievanceSteps.Lookup) {
        errors.selectedHousehold = `${beneficiaryGroup?.groupLabel} is Required`;
      }
      if (
        // xD
        values.selectedHousehold &&
        !values.householdDataUpdateFields?.[0]?.fieldName &&
        activeStep === GrievanceSteps.Description
      ) {
        errors.householdDataUpdateFields = `${beneficiaryGroup?.groupLabel} Data Change is Required`;
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
        errors.selectedIndividual = `${beneficiaryGroup?.memberLabel} is Required`;
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD) {
      if (!values.selectedHousehold && activeStep === GrievanceSteps.Lookup) {
        errors.selectedHousehold = `${beneficiaryGroup?.groupLabel} is Required`;
      }
    }
    if (issueType === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL) {
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
        errors.individualDataUpdateFields = `${beneficiaryGroup?.memberLabel} Data Change is Required`;
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
          // Handle nested structure: doc.value.{country, key, number}
          const docValue = doc.value || doc;
          if (!docValue.country || !docValue.key || !docValue.number) {
            errors.individualDataUpdateFieldsDocuments =
              'Document type, country and number are required';
          }
        });
      }
      if (values.individualDataUpdateFieldsDocumentsToEdit?.length) {
        values.individualDataUpdateFieldsDocumentsToEdit.forEach(
          (el, index) => {
            const doc = values.individualDataUpdateFieldsDocumentsToEdit[index];
            const docValue = doc.value || doc;
            if (!docValue.country || !docValue.key || !docValue.number) {
              errors.individualDataUpdateFieldsDocumentsToEdit =
                'Document type, country and number are required';
            }
          },
        );
      }
      if (values.individualDataUpdateFieldsIdentities?.length) {
        values.individualDataUpdateFieldsIdentities.forEach((el, index) => {
          const doc = values.individualDataUpdateFieldsIdentities[index];
          const docValue = doc.value || doc;
          const partner = docValue.partner || docValue.agency;
          if (!docValue.country || !partner || !docValue.number) {
            errors.individualDataUpdateFieldsIdentities =
              'Identity partner, country and number are required';
          }
        });
      }
      if (values.individualDataUpdateFieldsIdentitiesToEdit?.length) {
        values.individualDataUpdateFieldsIdentitiesToEdit.forEach(
          (el, index) => {
            const doc =
              values.individualDataUpdateFieldsIdentitiesToEdit[index];
            const docValue = doc.value || doc;
            const partner = docValue.partner || docValue.agency;
            if (!docValue.country || !partner || !docValue.number) {
              errors.individualDataUpdateFieldsIdentitiesToEdit =
                'Identity partner, country and number are required';
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
    category === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
    issueType === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL &&
    activeStep === GrievanceSteps.Description
  ) {
    const individualDataErrors = {};
    const individualData = values.individualData || {};

    if (addIndividualFieldsData) {
      for (const field of addIndividualFieldsData) {
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

    if (individualData?.documents?.length) {
      individualData.documents.forEach((_el, index) => {
        const doc = values.individualData.documents[index];
        const docValue = doc.value || doc;
        if (!docValue.country || !docValue.key || !docValue.number) {
          errors.individualDataUpdateFieldsDocuments =
            'Document type, country and number are required';
        }
      });
    }

    if (individualData?.identities?.length) {
      individualData.identities.forEach((_el, index) => {
        const doc = values.individualData.identities[index];
        const docValue = doc.value || doc;
        const partner = docValue.partner || docValue.agency;
        if (!docValue.country || !partner || !docValue.number) {
          errors.individualDataUpdateFieldsIdentities =
            'Identity partner, country and number are required';
        }
      });
    }
  }
  const householdRequiredGrievanceTypes = [
    GRIEVANCE_ISSUE_TYPES.PAYMENT_COMPLAINT,
    GRIEVANCE_ISSUE_TYPES.FSP_COMPLAINT,
  ];
  if (
    activeStep === GrievanceSteps.Lookup &&
    !values.selectedHousehold &&
    householdRequiredGrievanceTypes.includes(values.issueType)
  ) {
    errors.selectedHousehold = `${beneficiaryGroup?.groupLabel} is Required`;
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
      errors.selectedIndividual = `${beneficiaryGroup?.memberLabel} is Required`;
    } else if (isHouseholdRequired && !values.selectedHousehold) {
      errors.selectedHousehold = `${beneficiaryGroup?.groupLabel} is Required`;
    }
  }
  if (
    activeStep === GrievanceSteps.Verification &&
    (values.selectedHousehold ||
      (values.selectedIndividual && !values.verificationRequired))
  ) {
    // const MIN_SELECTED_ITEMS = 5;
    // const selectedItems = verficationStepFields.filter((item) => values[item]);
    // TODO: enable this when questionnaire verification is required
    // if (selectedItems.length < MIN_SELECTED_ITEMS) {
    //   setValidateData(true);
    //   errors.verificationRequired = 'Select correctly minimum 5 questions';
    // }
  }
  if (activeStep === GrievanceSteps.Description) {
    if (
      values.issueType === GRIEVANCE_ISSUE_TYPES.PAYMENT_COMPLAINT &&
      !Object.keys(values.selectedPaymentRecords).length
    ) {
      errors.selectedPaymentRecords = 'Payment Records are required';
    } else if (
      values.issueType === GRIEVANCE_ISSUE_TYPES.PARTNER_COMPLAINT &&
      !values.partner
    ) {
      errors.partner = 'Partner is required';
    }
    setValidateData(true);
  }

  if (values.documentation?.length) {
    values.documentation
      .filter((el) => el)
      .forEach((doc) => {
        if (!doc.name || !doc.file) {
          errors.documentation =
            'Grievance Supporting Document name and file are required';
        }
      });
  }

  return errors;
}
