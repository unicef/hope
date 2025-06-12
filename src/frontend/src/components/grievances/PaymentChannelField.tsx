import { Grid2 as Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { getIndexForId } from './utils/helpers';
import { ReactElement } from 'react';

export interface PaymentChannelFieldProps {
  id: string;
  baseName: string;
  onDelete;
  isEdited?: boolean;
  paymentChannel?: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['paymentChannels'][number];
  values;
}

export function PaymentChannelField({
  id,
  baseName,
  onDelete,
  isEdited,
  paymentChannel,
  values,
}: PaymentChannelFieldProps): ReactElement {
  const { t } = useTranslation();
  const paymentChannelFieldName = `${baseName}.${getIndexForId(
    values[baseName],
    id,
  )}`;
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
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
      <Grid size={{ xs: 4 }}>
        <LabelizedField
          label={t('Payment Channel Item')}
          value={t('Bank Account Number')}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <LabelizedField
          label={t('Current Value')}
          value={paymentChannel?.bankAccountNumber}
        />
      </Grid>
      <Grid size={{ xs: 3 }}>
        <Field
          name={`${paymentChannelFieldName}.bankAccountNumber`}
          fullWidth
          variant="outlined"
          label={t('New Value')}
          component={FormikTextField}
          required={!isEditTicket}
          disabled={isEditTicket}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <LabelizedField
          label={t('Payment Channel Item')}
          value={t('Bank Name')}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <LabelizedField
          label={t('Current Value')}
          value={paymentChannel?.bankName}
        />
      </Grid>
      <Grid size={{ xs: 3 }}>
        <Field
          name={`${paymentChannelFieldName}.bankName`}
          fullWidth
          variant="outlined"
          label={t('New Value')}
          component={FormikTextField}
          required={!isEditTicket}
          disabled={isEditTicket}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <LabelizedField
          label={t('Payment Channel Item')}
          value={t('Account Holder Name')}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <LabelizedField
          label={t('Current Value')}
          value={paymentChannel?.accountHolderName}
        />
      </Grid>
      <Grid size={{ xs: 3 }}>
        <Field
          name={`${paymentChannelFieldName}.accountHolderName`}
          fullWidth
          variant="outlined"
          label={t('New Value')}
          component={FormikTextField}
          required
          disabled={isEditTicket}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <LabelizedField
          label={t('Payment Channel Item')}
          value={t('Bank Branch Name')}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <LabelizedField
          label={t('Current Value')}
          value={paymentChannel?.bankBranchName}
        />
      </Grid>
      <Grid size={{ xs: 3 }}>
        <Field
          name={`${paymentChannelFieldName}.bankBranchName`}
          fullWidth
          variant="outlined"
          label={t('New Value')}
          component={FormikTextField}
          required
          disabled={isEditTicket}
        />
      </Grid>
    </>
  );
}
