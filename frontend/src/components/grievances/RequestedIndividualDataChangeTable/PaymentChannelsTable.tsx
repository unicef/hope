import {
  Box,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { GrievanceTicketQuery } from '@generated/graphql';
import { TableTitle } from '@core/TableTitle';
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
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  paymentChannels;
}

export function PaymentChannelsTable({
  values,
  isEdit,
  ticket,
  setFieldValue,
  paymentChannels,
}: PaymentChannelsTableProps): React.ReactElement {
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
        <TableCell align="left" />
        <TableCell data-cy="table-cell-bank-name" align="left">
          {t('Bank Name')}
        </TableCell>
        <TableCell data-cy="table-cell-bank-account-number" align="left">
          {t('Bank Account Number')}
        </TableCell>
        <TableCell data-cy="table-cell-bank-account-holder-name" align="left">
          {t('Bank Account Holder Name')}
        </TableCell>
        <TableCell data-cy="table-cell-bank-branch-name" align="left">
          {t('Bank Branch Name')}
        </TableCell>
      </TableRow>
    </TableHead>
  );

  return (
    <>
      <TableTitle>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">
            {t('Payment channels to be added')}
          </Typography>
        </Box>
      </TableTitle>
      <StyledTable>
        {paymentChannelsTableHead}
        <TableBody>
          {paymentChannels?.map((row, index) => (
            <TableRow
              key={`${row.value.bankName}-${row.value.bankAccountNumber}`}
            >
              <TableCell align="left">
                {isEdit ? (
                  <Checkbox
                    data-cy="checkbox-payment-channel"
                    color="primary"
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
                    <GreenIcon data-cy="green-check">
                      <CheckCircleIcon />
                    </GreenIcon>
                  )
                )}
              </TableCell>
              <TableCell align="left">{row.value.bank_name}</TableCell>
              <TableCell align="left">
                {row.value.bank_account_number}
              </TableCell>
              <TableCell align="left">
                {row.value.account_holder_name}
              </TableCell>
              <TableCell align="left">{row.value.bank_branch_name}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </StyledTable>
    </>
  );
}
