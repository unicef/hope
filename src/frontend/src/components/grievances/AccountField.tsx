import { Grid2 as Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { getIndexForId } from './utils/helpers';
import { Fragment, ReactElement } from 'react';


export interface AccountProps {
  id: string;
  baseName: string;
  onDelete;
  isEdited?: boolean;
  account?: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['accounts'][number];
  values;
}

export function AccountField({
  id,
  baseName,
  onDelete,
  isEdited,
  account,
  values,
}: AccountProps): ReactElement {
  const { t } = useTranslation();
  const accountFieldName = `${baseName}.${getIndexForId(
    values[baseName],
    id,
  )}`;
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const dataFields = account.dataFields ? JSON.parse(account.dataFields) : {};

  return (
    <>
      <Grid size={{ xs: 11 }} />
      {!isEdited ? (
        <Grid size={{ xs: 1 }}>
          <IconButton disabled={isEditTicket} onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      ) : null}
     {Object.entries(dataFields).map(([key, value]) => (
        <Fragment key={key}>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Account Item')}
              value={String(key)}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Current Value')}
              value={String(value)}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Field
              name={`${accountFieldName}.${key}`}
              fullWidth
              variant="outlined"
              label={t('New Value')}
              component={FormikTextField}
              required={!isEditTicket}
              disabled={isEditTicket}
            />
          </Grid>
        </Fragment>
      ))}
    </>
  );
}