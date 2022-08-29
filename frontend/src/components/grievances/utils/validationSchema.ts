import * as Yup from 'yup';
import { GrievanceSteps } from '../../../utils/constants';

export const validationSchema = Yup.object().shape({
  description: Yup.string().required('Description is required'),
  assignedTo: Yup.string().required('Assigned To is required'),
  category: Yup.string()
    .required('Category is required')
    .nullable(),
  admin: Yup.string().nullable(),
  area: Yup.string(),
  language: Yup.string(),
  consent: Yup.bool().oneOf([true], 'Consent is required'),
  selectedPaymentRecords: Yup.array()
    .of(Yup.string())
    .nullable(),
  selectedRelatedTickets: Yup.array()
    .of(Yup.string())
    .nullable(),
});

export const validationSchemaWithSteps = (currentStep: number): unknown => {
  const datum = {
    category: Yup.string()
      .required('Category is required')
      .nullable(),
    admin: Yup.string().nullable(),
    description: Yup.string(),
    consent: Yup.bool(),
    area: Yup.string(),
    language: Yup.string(),
    selectedPaymentRecords: Yup.array()
      .of(Yup.string())
      .nullable(),
    selectedRelatedTickets: Yup.array()
      .of(Yup.string())
      .nullable(),
  };

  if (currentStep === GrievanceSteps.Description) {
    datum.description = Yup.string().required('Description is required');
  }

  if (currentStep >= GrievanceSteps.Verification) {
    datum.consent = Yup.bool().oneOf([true], 'Consent is required');
  }

  const validationSchema3 = Yup.object().shape(datum);

  return validationSchema3;
};
