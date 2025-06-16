import { Grid2 as Grid } from '@mui/material';
import { Field } from 'formik';
import { useLocation } from 'react-router-dom';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikDecimalField } from '@shared/Formik/FormikDecimalField';
import { FormikFileField } from '@shared/Formik/FormikFileField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikBoolFieldGrievances } from '../FormikBoolFieldGrievances';
import { GrievanceFlexFieldPhotoModalEditable } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModalEditable';
import { ReactElement } from 'react';

export interface EditIndividualDataChangeFieldProps {
  field: {
    name?: string;
    type?: string;
    labelEn?: string;
    required?: boolean;
    choices?: Array<{
      value: any;
      labelEn?: string;
    }>;
  };
  name: string;
}
export const EditIndividualDataChangeField = ({
  name,
  field,
}: EditIndividualDataChangeFieldProps): ReactElement => {
  const location = useLocation();
  const isNewTicket = location.pathname.indexOf('new-ticket') !== -1;
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;

  let fieldProps;
  if (!field) return null;

  switch (field.type) {
    case 'DECIMAL':
      fieldProps = {
        fullWidth: true,
        component: FormikDecimalField,
      };
      break;
    case 'INTEGER':
      fieldProps = {
        component: FormikTextField,
        type: 'number',
      };
      break;
    case 'STRING':
      fieldProps = {
        fullWidth: true,
        component: FormikTextField,
      };
      break;
    case 'SELECT_ONE':
      fieldProps = {
        choices: field.choices,
        fullWidth: true,
        component: FormikSelectField,
      };
      break;
    case 'SELECT_MANY':
      fieldProps = {
        choices: field.choices,
        fullWidth: true,
        component: FormikSelectField,
        multiple: true,
      };
      break;
    case 'SELECT_MULTIPLE':
      fieldProps = {
        choices: field.choices,
        fullWidth: true,
        component: FormikSelectField,
      };
      break;
    case 'DATE':
      fieldProps = {
        component: FormikDateField,
        fullWidth: true,
        decoratorEnd: <CalendarTodayRoundedIcon color="disabled" />,
      };
      break;

    case 'BOOL':
      fieldProps = {
        component: FormikBoolFieldGrievances,
        required: field.required,
      };
      break;
    case 'IMAGE':
      fieldProps = {
        component: isNewTicket
          ? FormikFileField
          : GrievanceFlexFieldPhotoModalEditable,
        flexField: field,
        isIndividual: true,
      };
      break;
    default:
      fieldProps = {};
  }
  return (
    <Grid size={{ xs: 4 }}>
      <Field
        name={name}
        variant="outlined"
        label={field.labelEn}
        required={field.required}
        data-cy={`input-individual-data-${field.labelEn}`}
        disabled={isEditTicket}
        {...fieldProps}
      />
    </Grid>
  );
};
