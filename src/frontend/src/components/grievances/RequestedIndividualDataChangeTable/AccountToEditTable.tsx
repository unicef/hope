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

const GreenIcon = styled.div`
  color: #28cb15;
`;
const GreyText = styled.div`
  color: #9e9e9e;
`;

const StyledTable = styled(Table)`
  min-width: 100px;
`;

export interface AccountToEditTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketDetail;
  setFieldValue;
  index;
  account;
  accountFinancialInstitutionsDict;
}

export function AccountToEditTable({
  values,
  isEdit,
  ticket,
  setFieldValue,
  index,
  account,
  accountFinancialInstitutionsDict,
}: AccountToEditTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedAccountsToEdit } = values;
  const handleSelectAccountsToEdit = (accountIndex): void => {
    handleSelected(
      accountIndex,
      'selectedAccountsToEdit',
      selectedAccountsToEdit,
      setFieldValue,
    );
  };
  const renderNewOrNotUpdated = (prev, curr): ReactElement => {
    if (prev === curr) {
      return <GreyText>{t('Not updated')}</GreyText>;
    }
    return <span>{curr}</span>;
  };

  return (
    <>
      <TableTitle>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">
            {t('Account to be edited')} - {account.accountType}
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
                  data-cy="checkbox-edit-account"
                  onChange={(): void => {
                    handleSelectAccountsToEdit(index);
                  }}
                  disabled={
                    ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                  }
                  checked={selectedAccountsToEdit.includes(index)}
                  inputProps={{ 'aria-labelledby': 'selected' }}
                />
              ) : (
                selectedAccountsToEdit.includes(index) && (
                  <GreenIcon data-cy="green-check">
                    <CheckCircleIcon />
                  </GreenIcon>
                )
              )}
            </TableCell>
            <TableCell align="left">{t('Field')}</TableCell>
            <TableCell align="left">{t('Current Value')}</TableCell>
            <TableCell align="left">{t('New Value')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow key="number">
            <TableCell align="left"></TableCell>
            <TableCell align="left">Number</TableCell>
            <TableCell align="left">
              {account.numberPreviousValue || '-'}
            </TableCell>
            <TableCell align="left">
              {renderNewOrNotUpdated(
                account.numberPreviousValue,
                account.number,
              )}
            </TableCell>
          </TableRow>
          <TableRow key="financial_institution">
            <TableCell align="left"></TableCell>
            <TableCell align="left">Financial Institution</TableCell>
            <TableCell align="left">
              {accountFinancialInstitutionsDict[
                account.financialInstitutionPreviousValue
              ] || '-'}
            </TableCell>
            <TableCell align="left">
              {renderNewOrNotUpdated(
                accountFinancialInstitutionsDict[
                  account.financialInstitutionPreviousValue
                ],
                accountFinancialInstitutionsDict[account.financialInstitution],
              )}
            </TableCell>
          </TableRow>
          {account.dataFields.map((field, fieldIndex) => {
            return (
              <TableRow key={fieldIndex}>
                <TableCell align="left"></TableCell>
                <TableCell align="left">{field.name}</TableCell>
                <TableCell align="left">{field.previousValue || '-'}</TableCell>
                <TableCell align="left">
                  {renderNewOrNotUpdated(field.previousValue, field.value)}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </StyledTable>
    </>
  );
}
