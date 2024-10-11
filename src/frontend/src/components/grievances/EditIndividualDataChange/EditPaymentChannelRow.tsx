import { Box, Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import Close from '@mui/icons-material/Close';
import { useLocation } from 'react-router-dom';
import Edit from '@mui/icons-material/Edit';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { PaymentChannelField } from '../PaymentChannelField';
import { removeItemById } from '../utils/helpers';

interface DisabledDivProps {
  disabled: boolean;
}

const DisabledDiv = styled.div<DisabledDivProps>`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;

export interface EditPaymentChannelRowProps {
  setFieldValue;
  values;
  paymentChannel: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['paymentChannels'][number];
  arrayHelpers;
  id: string;
}

export function EditPaymentChannelRow({
  setFieldValue,
  values,
  paymentChannel,
  arrayHelpers,
  id,
}: EditPaymentChannelRowProps): React.ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.includes('edit-ticket');
  const { t } = useTranslation();
  const [isEdited, setEdit] = useState(false);
  const toRemove = values?.individualDataUpdatePaymentChannelsToRemove || [];
  const removed = toRemove.includes(paymentChannel.id);
  return isEdited ? (
    <>
      <PaymentChannelField
        id={id}
        key={`${id}-${paymentChannel.id}`}
        onDelete={() =>
          removeItemById(
            values.individualDataUpdatePaymentChannelsToRemove,
            paymentChannel.id,
            arrayHelpers,
          )
        }
        baseName="individualDataUpdatePaymentChannelsToEdit"
        isEdited={isEdited}
        paymentChannel={paymentChannel}
        values={values}
      />
      <Box display="flex" alignItems="center">
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
      <Grid item xs={3}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('Bank name')}
            value={paymentChannel.bankName}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={2}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('Account holder name')}
            value={paymentChannel.accountHolderName}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={2}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('Bank branch name')}
            value={paymentChannel.bankBranchName}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={1}>
        {!removed ? (
          <Box display="flex" align-items="center">
            <IconButton
              onClick={() => {
                setFieldValue(
                  `individualDataUpdatePaymentChannelsToRemove[${toRemove.length}]`,
                  paymentChannel.id,
                );
              }}
              disabled={isEditTicket}
            >
              <Delete />
            </IconButton>
            <IconButton
              onClick={() => {
                arrayHelpers.push({
                  id: paymentChannel.id,
                  bankName: paymentChannel.bankName,
                  bankAccountNumber: paymentChannel.bankAccountNumber,
                  accountHolderName: paymentChannel.accountHolderName,
                  bankBranchName: paymentChannel.bankBranchName,
                  type: 'BANK_TRANSFER',
                });
                setEdit(true);
              }}
              disabled={isEditTicket}
            >
              <Edit />
            </IconButton>
          </Box>
        ) : (
          <Box display="flex" alignItems="center" height={48} color="red">
            {t('REMOVED')}
          </Box>
        )}
      </Grid>
    </React.Fragment>
  );
}
