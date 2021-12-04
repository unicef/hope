import { Grid } from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field } from 'formik';
import React from 'react';
import { useLocation } from 'react-router-dom';
import { FormikDateField } from '../../../shared/Formik/FormikDateField';
import { FormikDecimalField } from '../../../shared/Formik/FormikDecimalField';
import { FormikFileField } from '../../../shared/Formik/FormikFileField';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { AllEditHouseholdFieldsQuery } from '../../../__generated__/graphql';
import { FormikBoolFieldGrievances } from '../FormikBoolFieldGrievances';
import { GrievanceFlexFieldPhotoModalEditable } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModalEditable';

export interface EditHouseholdDataChangeField {
  field: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'][number];
  name: string;
}
export const EditHouseholdDataChangeField = ({
  name,
  field,
}: EditHouseholdDataChangeField): React.ReactElement => {
  const location = useLocation();
  const isNewTicket = location.pathname.indexOf('new-ticket') !== -1;

  let fieldProps;
  switch (field.type) {
    case 'DECIMAL':
      fieldProps = {
        component: FormikDecimalField,
      };
      break;
    case 'STRING':
      fieldProps = {
        component: FormikTextField,
      };
      break;
    case 'INTEGER':
      fieldProps = {
        component: FormikTextField,
        type: 'number',
      };
      break;
    case 'SELECT_ONE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'SELECT_MANY':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
        multiple: true,
      };
      break;
    case 'SELECT_MULTIPLE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'DATE':
      fieldProps = {
        component: FormikDateField,
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
        isIndividual: false,
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
          fullWidth
          variant='outlined'
          label={field.labelEn}
          required={field.required}
          {...fieldProps}
        />
      </Grid>
    </>
  );
};
