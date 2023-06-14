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
import {
  AllEditHouseholdFieldsQuery,
  useAllAdminAreasLazyQuery,
} from '../../../__generated__/graphql';
import { FormikBoolFieldGrievances } from '../FormikBoolFieldGrievances';
import { GrievanceFlexFieldPhotoModalEditable } from '../GrievancesPhotoModals/GrievanceFlexFieldPhotoModalEditable';
import { FormikAutocomplete } from '../../../shared/Formik/FormikAutocomplete';
import { FormikAsyncAutocomplete } from '../../../shared/Formik/FormikAsyncAutocomplete';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

export interface EditHouseholdDataChangeField {
  field: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'][number];
  name: string;
}
export const EditHouseholdDataChangeField = ({
  name,
  field,
}: EditHouseholdDataChangeField): React.ReactElement => {
  const businessArea = useBusinessArea();
  const location = useLocation();
  const isNewTicket = location.pathname.indexOf('new-ticket') !== -1;
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  let fieldProps;
  if (!field) return null;

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
        component: FormikAutocomplete,
      };
      if (field.name === 'admin_area_title') {
        fieldProps = {
          component: FormikAsyncAutocomplete,
          query: useAllAdminAreasLazyQuery,
          fetchData: (data) =>
            data?.allAdminAreas?.edges?.map(({ node }) => ({
              labelEn: `${node.name} - ${node.pCode}`,
              value: node.pCode,
            })),
          variables: {
            businessArea,
          },
        };
      } else {
        fieldProps = {
          choices: field.choices,
          component: FormikSelectField,
        };
      }
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
          disabled={isEditTicket}
          {...fieldProps}
        />
      </Grid>
    </>
  );
};
