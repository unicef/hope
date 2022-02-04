import { Grid } from '@material-ui/core';
import { Field } from 'formik';
import { useLocation } from 'react-router-dom';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import React from 'react';
import { FormikDateField } from '../../../shared/Formik/FormikDateField';
import { FormikDecimalField } from '../../../shared/Formik/FormikDecimalField';
import { FormikFileField } from '../../../shared/Formik/FormikFileField';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { AllAddIndividualFieldsQuery } from '../../../__generated__/graphql';
import { FormikBoolFieldGrievances } from '../FormikBoolFieldGrievances';
import { GrievanceFlexFieldPhotoModalEditable } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModalEditable';

export interface EditIndividualDataChangeField {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  name: string;
}
export const EditIndividualDataChangeField = ({
  name,
  field,
}: EditIndividualDataChangeField): React.ReactElement => {
  const location = useLocation();
  const isNewTicket = location.pathname.indexOf('new-ticket') !== -1;
  let fieldProps;
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
        decoratorEnd: <CalendarTodayRoundedIcon color='disabled' />,
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
    <>
      <Grid item xs={4}>
        <Field
          name={name}
          variant='outlined'
          label={field.labelEn}
          required={field.required}
          {...fieldProps}
        />
      </Grid>
    </>
  );
};
