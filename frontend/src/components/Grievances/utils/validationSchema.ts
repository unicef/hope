import * as Yup from 'yup';

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
