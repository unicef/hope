import { Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { AllAddIndividualFieldsQuery } from '@generated/graphql';
import { getIndexForId } from './utils/helpers';

export interface AgencyFieldProps {
  id: string;
  baseName: string;
  baseNameArray?;
  onDelete;
  countryChoices: AllAddIndividualFieldsQuery['countriesChoices'];
  identityTypeChoices: AllAddIndividualFieldsQuery['identityTypeChoices'];
  isEdited?: boolean;
  values;
}

export function AgencyField({
  id,
  baseName,
  baseNameArray,
  onDelete,
  countryChoices,
  identityTypeChoices,
  isEdited,
  values,
}: AgencyFieldProps): React.ReactElement {
  const { t } = useTranslation();
  const agencyFieldName = `${baseName}.${getIndexForId(
    baseNameArray || values[baseName],
    id,
  )}`;

  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <>
      <Grid item xs={4}>
        <Field
          name={`${agencyFieldName}.partner`}
          fullWidth
          variant="outlined"
          label={t('Partner')}
          component={FormikSelectField}
          choices={identityTypeChoices}
          required
          disabled={isEditTicket}
        />
      </Grid>
      <Grid item xs={4}>
        <Field
          name={`${agencyFieldName}.country`}
          fullWidth
          variant="outlined"
          label={t('Country')}
          component={FormikSelectField}
          choices={countryChoices}
          required
          disabled={isEditTicket}
        />
      </Grid>
      <Grid item xs={3}>
        <Field
          name={`${agencyFieldName}.number`}
          fullWidth
          variant="outlined"
          label={t('Identity Number')}
          component={FormikTextField}
          required
          disabled={isEditTicket}
        />
      </Grid>
      {!isEdited ? (
        <Grid item xs={1}>
          <IconButton disabled={isEditTicket} onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      ) : null}
    </>
  );
}
