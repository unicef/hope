import { Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { AllIndividualsQuery } from '../../__generated__/graphql';
import { LabelizedField } from '../core/LabelizedField';

export interface PaymentChannelProps {
  index: number;
  baseName: string;
  onDelete: () => {};
  isEdited?: boolean;
  paymentChannel?: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['paymentChannels'][number];
}

export function PaymentChannelField({
  index,
  baseName,
  onDelete,
  isEdited,
  paymentChannel,
}: PaymentChannelProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <>
      <Grid item xs={11} />
      {!isEdited ? (
        <Grid item xs={1}>
          <IconButton onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      ) : null}
      <Grid item xs={4}>
        <LabelizedField label={t('Payment channel item')} value='IBAN' />
      </Grid>
      <Grid item xs={4}>
        <LabelizedField
          label={t('Current Value')}
          value={paymentChannel?.bankAccountNumber}
        />
      </Grid>
      <Grid item xs={3}>
        <Field
          name={`${baseName}[${index}].bankAccountNumber`}
          fullWidth
          variant='outlined'
          label={t('New Value')}
          component={FormikTextField}
          required
        />
      </Grid>
      <Grid item xs={4}>
        <LabelizedField
          label={t('Payment channel item')}
          value={t('Bank name')}
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
          name={`${baseName}[${index}].bankName`}
          fullWidth
          variant='outlined'
          label={t('New Value')}
          component={FormikTextField}
          required
        />
      </Grid>
    </>
  );
}
