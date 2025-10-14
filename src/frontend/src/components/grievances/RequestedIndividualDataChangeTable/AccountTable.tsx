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
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { TableTitle } from '@core/TableTitle';
import { handleSelected } from '../utils/helpers';
import { ReactElement } from 'react';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { safeStringify } from '@utils/utils';

const GreenIcon = styled.div`
  color: #28cb15;
`;

const StyledTable = styled(Table)`
  min-width: 100px;
`;

function camelToTitle(input: string): string {
  const parts = input
    .replace(/[_-]+/g, ' ')
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
    .trim()
    .split(/\s+/);

  return parts
    .map((p) =>
      /^[A-Z0-9]{2,}$/.test(p)
        ? p
        : p.charAt(0).toUpperCase() + p.slice(1).toLowerCase(),
    )
    .join(' ');
}

export interface AccountsTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketDetail;
  setFieldValue;
  index;
  account;
  accountFinancialInstitutionsDict;
}

export function AccountTable({
  values,
  isEdit,
  ticket,
  setFieldValue,
  index,
  account,
  accountFinancialInstitutionsDict,
}: AccountsTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedAccounts } = values;

  const handleSelectAccount = (idx): void => {
    handleSelected(idx, 'selectedAccounts', selectedAccounts, setFieldValue);
  };

  return (
    <>
      <TableTitle>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">
            {t('Account to be created')} - {account.value.accountType}
          </Typography>
        </Box>
      </TableTitle>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align="left">
              {isEdit ? (
                <Checkbox
                  color="primary"
                  data-cy="checkbox-create-account"
                  onChange={(): void => {
                    handleSelectAccount(index);
                  }}
                  disabled={
                    ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                  }
                  checked={selectedAccounts.includes(index)}
                  inputProps={{ 'aria-labelledby': 'selected' }}
                />
              ) : (
                selectedAccounts.includes(index) && (
                  <GreenIcon data-cy="green-check">
                    <CheckCircleIcon />
                  </GreenIcon>
                )
              )}
            </TableCell>
            <TableCell align="left">{t('Field')}</TableCell>
            <TableCell align="left">{t('Value')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.entries(account.value || {})
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            .filter(([key, _]) => key !== 'accountType')
            .map(([key, value]) => {
              if (key === 'financialInstitution') {
                value = accountFinancialInstitutionsDict[value as string];
              }
              return (
                <TableRow key={key}>
                  <TableCell align="left"></TableCell>
                  <TableCell align="left">{camelToTitle(key)}</TableCell>
                  <TableCell align="left">{safeStringify(value)}</TableCell>
                  <TableCell align="left"></TableCell>
                </TableRow>
              );
            })}
        </TableBody>
      </StyledTable>
    </>
  );
}
