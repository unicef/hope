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
const GreyText = styled.div`
  color: #9e9e9e;
`;

const StyledTable = styled(Table)`
  min-width: 100px;
`;

export interface PaymentChannelsToEditTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  index;
  paymentChannel;
}

export const PaymentChannelsToEditTable = ({
  values,
  isEdit,
  ticket,
  setFieldValue,
  index,
  paymentChannel,
}: PaymentChannelsToEditTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const { selectedPaymentChannelsToEdit } = values;
  const handleSelectPaymentChannelToEdit = (paymentChannelIndex): void => {
    handleSelected(
      paymentChannelIndex,
      'selectedPaymentChannelsToEdit',
      selectedPaymentChannelsToEdit,
      setFieldValue,
    );
  };
  const renderNewOrNotUpdated = (prev, curr): React.ReactElement => {
    if (prev === curr) {
      return <GreyText>{t('Not updated')}</GreyText>;
    }
    return <span>{curr}</span>;
  };

  return (
    <>
      <TableTitle>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>
            {t('Payment channel to be edited')}
          </Typography>
        </Box>
      </TableTitle>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align='left'>
              {isEdit ? (
                <Checkbox
                  color='primary'
                  onChange={(): void => {
                    handleSelectPaymentChannelToEdit(index);
                  }}
                  disabled={
                    ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                  }
                  checked={selectedPaymentChannelsToEdit.includes(index)}
                  inputProps={{ 'aria-labelledby': 'selected' }}
                />
              ) : (
                selectedPaymentChannelsToEdit.includes(index) && (
                  <GreenIcon>
                    <CheckCircleIcon />
                  </GreenIcon>
                )
              )}
            </TableCell>
            <TableCell align='left'>{t('Field')}</TableCell>
            <TableCell align='left'>{t('Current Value')}</TableCell>
            <TableCell align='left'>{t('New Value')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell />
            <TableCell align='left'>{t('Bank name')}</TableCell>
            <TableCell align='left'>
              {paymentChannel.previous_value.bank_name}
            </TableCell>
            <TableCell align='left'>
              {renderNewOrNotUpdated(
                paymentChannel.previous_value?.bank_name,
                paymentChannel.value?.bank_name,
              )}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align='left'>{t('Bank account number')}</TableCell>
            <TableCell align='left'>
              {paymentChannel.previous_value.bank_account_number}
            </TableCell>
            <TableCell align='left'>
              {renderNewOrNotUpdated(
                paymentChannel.previous_value?.bank_account_number,
                paymentChannel.value?.bank_account_number,
              )}
            </TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </>
  );
};
