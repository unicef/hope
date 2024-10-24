import * as Yup from 'yup';
import { GrievanceSteps, GRIEVANCE_ISSUE_TYPES } from '@utils/constants';

const selectedPaymentRecordsScheme = Yup.array()
  .of(
    Yup.object().shape({
      id: Yup.string(),
      caId: Yup.string(),
    }),
  )
  .nullable();

export const validationSchema = Yup.object().shape({
  description: Yup.string().required('Description is required'),
  category: Yup.string().required('Category is required').nullable(),
  admin: Yup.string().nullable(),
  area: Yup.string(),
  language: Yup.string(),
  consent: Yup.bool().oneOf([true], 'Consent is required'),
  selectedPaymentRecords: selectedPaymentRecordsScheme,
  selectedLinkedTickets: Yup.array().of(Yup.string()).nullable(),
});

export const validationSchemaWithSteps = (currentStep: number): unknown => {
  const datum = {
    category: Yup.string().required('Category is required').nullable(),
    issueType: Yup.string().nullable(),
    admin: Yup.string().nullable(),
    description: Yup.string(),
    consent: Yup.bool(),
    area: Yup.string(),
    language: Yup.string(),
    selectedPaymentRecords: selectedPaymentRecordsScheme,
    selectedRelatedTickets: Yup.array().of(Yup.string()).nullable(),
  } as any;

  if (currentStep === GrievanceSteps.Description) {
    datum.description = Yup.string().required(
      datum.issueType === GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD ||
        datum.issueType === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL
        ? 'Withdrawal Reason is required'
        : 'Description is required',
    );
  }

  if (currentStep >= GrievanceSteps.Verification) {
    datum.consent = Yup.bool().oneOf([true], 'Consent is required');
  }

  return Yup.object().shape(datum);
};
