import { Box, Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import Close from '@material-ui/icons/Close';
import Edit from '@material-ui/icons/Edit';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { AllIndividualsQuery } from '../../../__generated__/graphql';
import { LabelizedField } from '../../core/LabelizedField';
import { PaymentChannelField } from '../PaymentChannelField';

const DisabledDiv = styled.div`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;

export interface EditPaymentChannelRowProps {
  setFieldValue;
  values;
  paymentChannel: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['paymentChannels'][number];
  arrayHelpers;
  index;
}

export function EditPaymentChannelRow({
  setFieldValue,
  values,
  paymentChannel,
  arrayHelpers,
  index,
}: EditPaymentChannelRowProps): React.ReactElement {
  const { t } = useTranslation();
  const [isEdited, setEdit] = useState(false);
  const toRemove = values?.individualDataUpdatePaymentChannelsToRemove || [];
  const removed = toRemove.includes(paymentChannel.id);
  return isEdited ? (
    <>
      <PaymentChannelField
        index={index}
        key={`${index}-${paymentChannel.id}`}
        onDelete={() => arrayHelpers.remove(index)}
        baseName='individualDataUpdatePaymentChannelsToEdit'
        isEdited={isEdited}
        paymentChannel={paymentChannel}
      />
      <Box display='flex' alignItems='center'>
        <IconButton
          onClick={() => {
            arrayHelpers.remove({
              bankAccountNumber: paymentChannel.bankAccountNumber,
              bankName: paymentChannel.bankName,
              type: 'BANK_TRANSFER',
            });
            setEdit(false);
          }}
        >
          <Close />
        </IconButton>
      </Box>
    </>
  ) : (
    <React.Fragment key={paymentChannel.id}>
      <Grid item xs={4}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('Bank account number')}
            value={paymentChannel.bankAccountNumber}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={4}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('Bank name')}
            value={paymentChannel.bankName}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={1}>
        {!removed ? (
          <Box display='flex' align-items='center'>
            <IconButton
              onClick={() => {
                setFieldValue(
                  `individualDataUpdatePaymentChannelsToRemove[${toRemove.length}]`,
                  paymentChannel.id,
                );
              }}
            >
              <Delete />
            </IconButton>
            <IconButton
              onClick={() => {
                arrayHelpers.replace(index, {
                  id: paymentChannel.id,
                  bankName: paymentChannel.bankName,
                  bankAccountNumber: paymentChannel.bankAccountNumber,
                  type: 'BANK_TRANSFER',
                });
                setEdit(true);
              }}
            >
              <Edit />
            </IconButton>
          </Box>
        ) : (
          <Box display='flex' alignItems='center' height={48} color='red'>
            {t('REMOVED')}
          </Box>
        )}
      </Grid>
    </React.Fragment>
  );
}
