import {Grid, IconButton} from '@material-ui/core';
import {Delete} from '@material-ui/icons';
import {Field} from 'formik';
import React from 'react';
import {FormikSelectField} from '../../shared/Formik/FormikSelectField';
import {FormikTextField} from '../../shared/Formik/FormikTextField';
import {AllAddIndividualFieldsQuery} from '../../__generated__/graphql';

export interface AgencyFieldProps {
  index: number;
  baseName: string;
  onDelete: () => {};
  countryChoices: AllAddIndividualFieldsQuery['countriesChoices'];
  identityTypeChoices: AllAddIndividualFieldsQuery['identityTypeChoices'];
}

export function AgencyField({
  index,
  baseName,
  onDelete,
  countryChoices,
  identityTypeChoices,
}: AgencyFieldProps): React.ReactElement {
  return (
    <>
      <Grid item xs={4}>
        <Field
          name={`${baseName}[${index}].country`}
          fullWidth
          variant='outlined'
          label='Country'
          component={FormikSelectField}
          choices={countryChoices}
          required
        />
      </Grid>
      <Grid item xs={4}>
        <Field
          name={`${baseName}[${index}].agency`}
          fullWidth
          variant='outlined'
          label='Agency'
          component={FormikSelectField}
          choices={identityTypeChoices}
          required
        />
      </Grid>
      <Grid item xs={3}>
        <Field
          name={`${baseName}[${index}].number`}
          fullWidth
          variant='outlined'
          label='Identity Number'
          component={FormikTextField}
          required
        />
      </Grid>
      <Grid item xs={1}>
        <IconButton onClick={onDelete}>
          <Delete />
        </IconButton>
      </Grid>
    </>
  );
}
