import {
  Box,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GRIEVANCE_TICKET_STATES } from '../../../utils/constants';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { TableTitle } from '../../core/TableTitle';
import { handleSelected } from '../utils/helpers';

const GreenIcon = styled.div`
  color: #28cb15;
`;
const StyledTable = styled(Table)`
  min-width: 100px;
`;

export interface PaymentChannelsToRemoveTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  paymentChannelsToRemove;
  previousPaymentChannels;
}

export const PaymentChannelsToRemoveTable = ({
  values,
  isEdit,
  ticket,
  paymentChannelsToRemove,
  previousPaymentChannels,
  setFieldValue,
}: PaymentChannelsToRemoveTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const { selectedPaymentChannelsToRemove } = values;
  const paymentChannelsTableHead = (
    <TableHead>
      <TableRow>
        <TableCell align='left' />
        <TableCell align='left'>{t('Bank name')}</TableCell>
        <TableCell align='left'>{t('Bank account number')}</TableCell>
      </TableRow>
    </TableHead>
  );
  const handleSelectPaymentChannelToRemove = (paymentChannelIndex): void => {
    handleSelected(
      paymentChannelIndex,
      'selectedPaymentChannelsToRemove',
      selectedPaymentChannelsToRemove,
      setFieldValue,
    );
  };

  return (
    <>
      <TableTitle>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>
            {t('Payment channels to be removed')}
          </Typography>
        </Box>
      </TableTitle>
      <StyledTable>
        {paymentChannelsTableHead}
        <TableBody>
          {paymentChannelsToRemove?.map((row, index) => {
            const paymentChannel = previousPaymentChannels[row.value];
            return (
              <TableRow
                key={`${paymentChannel.bank_name}-${paymentChannel.bank_account_number}`}
              >
                <TableCell align='left'>
                  {isEdit ? (
                    <Checkbox
                      onChange={(): void => {
                        handleSelectPaymentChannelToRemove(index);
                      }}
                      color='primary'
                      disabled={
                        ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                      }
                      checked={selectedPaymentChannelsToRemove.includes(index)}
                      inputProps={{ 'aria-labelledby': 'xd' }}
                    />
                  ) : (
                    selectedPaymentChannelsToRemove.includes(index) && (
                      <GreenIcon>
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </TableCell>
                <TableCell align='left'>
                  {paymentChannel?.bank_name || '-'}
                </TableCell>
                <TableCell align='left'>
                  {paymentChannel?.bank_account_number || '-'}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </StyledTable>
    </>
  );
};
