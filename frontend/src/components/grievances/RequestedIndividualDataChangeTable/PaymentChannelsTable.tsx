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
import { GrievanceTicketNode } from '../../../__generated__/graphql';
import { TableTitle } from '../../core/TableTitle';
import { handleSelected } from '../utils/helpers';

const GreenIcon = styled.div`
  color: #28cb15;
`;

const StyledTable = styled(Table)`
  min-width: 100px;
`;

export interface PaymentChannelsTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketNode;
  setFieldValue;
  paymentChannels;
}

export const PaymentChannelsTable = ({
  values,
  isEdit,
  ticket,
  setFieldValue,
  paymentChannels,
}: PaymentChannelsTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const { selectedPaymentChannels } = values;

  const handleSelectPaymentChannel = (index): void => {
    handleSelected(
      index,
      'selectedPaymentChannels',
      selectedPaymentChannels,
      setFieldValue,
    );
  };
  const paymentChannelsTableHead = (
    <TableHead>
      <TableRow>
        <TableCell align='left' />
        <TableCell align='left'>{t('Bank name')}</TableCell>
        <TableCell align='left'>{t('Bank account number')}</TableCell>
      </TableRow>
    </TableHead>
  );

  return (
    <>
      <TableTitle>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>
            {t('Payment channels to be added')}
          </Typography>
        </Box>
      </TableTitle>
      <StyledTable>
        {paymentChannelsTableHead}
        <TableBody>
          {paymentChannels?.map((row, index) => {
            return (
              <TableRow
                key={`${row.value.bankName}-${row.value.bankAccountNumber}`}
              >
                <TableCell align='left'>
                  {isEdit ? (
                    <Checkbox
                      color='primary'
                      onChange={(): void => {
                        handleSelectPaymentChannel(index);
                      }}
                      disabled={
                        ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                      }
                      checked={selectedPaymentChannels.includes(index)}
                      inputProps={{ 'aria-labelledby': 'selected' }}
                    />
                  ) : (
                    selectedPaymentChannels.includes(index) && (
                      <GreenIcon>
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </TableCell>
                <TableCell align='left'>{row.value.bank_name}</TableCell>
                <TableCell align='left'>
                  {row.value.bank_account_number}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </StyledTable>
    </>
  );
};
