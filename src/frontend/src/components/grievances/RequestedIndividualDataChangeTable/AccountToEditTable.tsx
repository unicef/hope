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
}

export function AccountToEditTable({
  values,
  isEdit,
  ticket,
  setFieldValue,
  index,
  account,
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
          {account.data_fields.map((field, fieldIndex) => (
            <TableRow key={fieldIndex}>
              <TableCell align="left"></TableCell>
              <TableCell align="left">{field.name}</TableCell>
              <TableCell align="left">{field.previous_value || '-'}</TableCell>
              <TableCell align="left">
                {renderNewOrNotUpdated(field.previous_value, field.value)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </StyledTable>
    </>
  );
}