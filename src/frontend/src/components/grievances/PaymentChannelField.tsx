import { Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { getIndexForId } from './utils/helpers';

export interface PaymentChannelProps {
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
}: PaymentChannelProps): React.ReactElement {
  const { t } = useTranslation();
  const paymentChannelFieldName = `${baseName}.${getIndexForId(
    values[baseName],
    id,
  )}`;
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <>
      <Grid item xs={11} />
      {!isEdited ? (
        <Grid item xs={1}>
          <IconButton disabled={isEditTicket} onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      ) : null}
      <Grid item xs={4}>
        <LabelizedField
          label={t('Payment Channel Item')}
          value={t('Bank Account Number')}
        />
      </Grid>
      <Grid item xs={4}>
        <LabelizedField
          label={t('Current Value')}
          value={paymentChannel?.bankAccountNumber}
        />
      </Grid>
      <Grid item xs={3}>
        <Field
          name={`${paymentChannelFieldName}.bankAccountNumber`}
          fullWidth
          variant="outlined"
          label={t('New Value')}
          component={FormikTextField}
          required
          disabled={isEditTicket}
        />
      </Grid>
      <Grid item xs={4}>
        <LabelizedField
          label={t('Payment Channel Item')}
          value={t('Bank Name')}
        />
      </Grid>
      <Grid item xs={4}>
        <LabelizedField
          label={t('Current Value')}
          value={paymentChannel?.bankName}
        />
      </Grid>
      <Grid item xs={3}>
        <Field
          name={`${paymentChannelFieldName}.bankName`}
          fullWidth
          variant="outlined"
          label={t('New Value')}
          component={FormikTextField}
          required
          disabled={isEditTicket}
        />
      </Grid>
      <Grid item xs={4}>
        <LabelizedField
          label={t('Payment Channel Item')}
          value={t('Account Holder Name')}
        />
      </Grid>
      <Grid item xs={4}>
        <LabelizedField
          label={t('Current Value')}
          value={paymentChannel?.accountHolderName}
        />
      </Grid>
      <Grid item xs={3}>
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
      <Grid item xs={4}>
        <LabelizedField
          label={t('Payment Channel Item')}
          value={t('Bank Branch Name')}
        />
      </Grid>
      <Grid item xs={4}>
        <LabelizedField
          label={t('Current Value')}
          value={paymentChannel?.bankBranchName}
        />
      </Grid>
      <Grid item xs={3}>
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
