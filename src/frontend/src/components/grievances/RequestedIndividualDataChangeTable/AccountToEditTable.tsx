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
import { GrievanceTicketQuery } from '@generated/graphql';
import { TableTitle } from '@core/TableTitle';
import { handleSelected } from '../utils/helpers';
import { ReactElement } from 'react';

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
  ticket: GrievanceTicketQuery['grievanceTicket'];
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
            {t('Account to be edited')} - {account.name}
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
            {account.data_fields.map(
              (field, fieldIndex) => {
                const isFinancialInstitutionField = field.name === 'financial_institution';
                const previousValue = isFinancialInstitutionField ? accountFinancialInstitutionsDict[field.previous_value] : field.previous_value;
                const newValue = isFinancialInstitutionField ? accountFinancialInstitutionsDict[field.value] : field.value;
                return (
                <TableRow key={fieldIndex}>
                  <TableCell align="left"></TableCell>
                  <TableCell align="left">{field.name}</TableCell>
                  <TableCell align="left">
                    {previousValue || '-'}
                  </TableCell>
                  <TableCell align="left">
                    {renderNewOrNotUpdated(
                      previousValue,
                      newValue,
                    )}
                  </TableCell>
                </TableRow>
              );
},
            )}
          </TableBody>
      </StyledTable>
    </>
  );
}