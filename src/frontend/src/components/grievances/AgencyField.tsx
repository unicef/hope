import { Grid2 as Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { AllAddIndividualFieldsQuery } from '@generated/graphql';
import { getIndexForId } from './utils/helpers';
import { ReactElement } from 'react';

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
}: AgencyFieldProps): ReactElement {
  const { t } = useTranslation();
  const agencyFieldName = `${baseName}.${getIndexForId(
    baseNameArray || values[baseName],
    id,
  )}`;

  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <Grid container alignItems="center" spacing={3}>
      <Grid size={{ xs: 4 }}>
        <Field
          name={`${agencyFieldName}.partner`}
          fullWidth
          variant="outlined"
          label={t('Partner')}
          component={FormikSelectField}
          choices={identityTypeChoices}
          required={!isEditTicket}
          disabled={isEditTicket}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <Field
          name={`${agencyFieldName}.country`}
          fullWidth
          variant="outlined"
          label={t('Country')}
          component={FormikSelectField}
          choices={countryChoices}
          required={!isEditTicket}
          disabled={isEditTicket}
        />
      </Grid>
      <Grid size={{ xs: 3 }}>
        <Field
          name={`${agencyFieldName}.number`}
          fullWidth
          variant="outlined"
          label={t('Identity Number')}
          component={FormikTextField}
          required={!isEditTicket}
          disabled={isEditTicket}
        />
      </Grid>
      {!isEdited ? (
        <Grid size={{ xs: 1 }}>
          <IconButton disabled={isEditTicket} onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      ) : null}
    </Grid>
  );
}
