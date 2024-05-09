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
const GreyText = styled.div`
  color: #9e9e9e;
`;

const StyledTable = styled(Table)`
  min-width: 100px;
`;

export interface DeliveryMechanismDataToEditTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  index;
  deliveryMechanismDataToEdit;
}

export function DeliveryMechanismDataToEditTable({
  values,
  isEdit,
  ticket,
  setFieldValue,
  index,
  deliveryMechanismDataToEdit,
}: DeliveryMechanismDataToEditTableProps): React.ReactElement {
  const { t } = useTranslation();
  const { selectedDeliveryMechanismDataToEdit } = values;
  const handleSelectDeliveryMechanismDataToEdit = (
    deliveryMechanismDataIndex,
  ): void => {
    handleSelected(
      deliveryMechanismDataIndex,
      'selectedDeliveryMechanismDataToEdit ',
      selectedDeliveryMechanismDataToEdit,
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
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">
            {t('Delivery Mechanism Data to be edited')}
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
                  data-cy="checkbox-edit-delivery-mechanism-data"
                  onChange={(): void => {
                    handleSelectDeliveryMechanismDataToEdit(index);
                  }}
                  disabled={
                    ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                  }
                  checked={selectedDeliveryMechanismDataToEdit.includes(index)}
                  inputProps={{ 'aria-labelledby': 'selected' }}
                />
              ) : (
                selectedDeliveryMechanismDataToEdit.includes(index) && (
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
          <TableRow>
            <TableCell />
            {/* <TableCell align="left">{t('Bank Name')}</TableCell>
            <TableCell align="left">
              {deliveryMechanismDataToEdit.previous_value.bank_name}
            </TableCell>
            <TableCell align="left">
              {renderNewOrNotUpdated(
                deliveryMechanismDataToEdit.previous_value?.bank_name,
                deliveryMechanismDataToEdit.value?.bank_name,
              )}
            </TableCell> */}
          </TableRow>
        </TableBody>
      </StyledTable>
    </>
  );
}
