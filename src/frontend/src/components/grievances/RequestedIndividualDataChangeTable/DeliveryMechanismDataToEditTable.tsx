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

export interface DeliveryMechanismDataToEditTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  index;
  deliveryMechanismDataToEdit;
}

export const DeliveryMechanismDataToEditTable = ({
  values,
  isEdit,
  ticket,
  setFieldValue,
  index,
  deliveryMechanismDataToEdit,
}: DeliveryMechanismDataToEditTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const { selectedDeliveryMechanismDataToEdit } = values;
  const handleSelectDeliveryMechanismDataToEdit = (
    deliveryMechanismDataIndex,
  ): void => {
    handleSelected(
      deliveryMechanismDataIndex,
      'selectedDeliveryMechanismDataToEdit',
      selectedDeliveryMechanismDataToEdit,
      setFieldValue,
    );
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
      <>
        <Box style={{ position: 'relative', top: '15px' }}>
          <Typography variant="subtitle2">
            {deliveryMechanismDataToEdit.label}
          </Typography>
        </Box>
        <StyledTable>
          <TableHead>
            <TableRow>
              <TableCell style={{ width: '1%' }} align="left">
                <div style={{ display: 'flex', alignItems: 'center' }}>
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
                      checked={selectedDeliveryMechanismDataToEdit.includes(
                        index,
                      )}
                      inputProps={{ 'aria-labelledby': 'selected' }}
                    />
                  ) : (
                    selectedDeliveryMechanismDataToEdit.includes(index) && (
                      <GreenIcon data-cy="green-check">
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </div>
              </TableCell>
              <TableCell align="left">{t('Field')}</TableCell>
              <TableCell align="left">{t('Previous Value')}</TableCell>
              <TableCell align="left">{t('New Value')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {deliveryMechanismDataToEdit.data_fields.map(
              (field, fieldIndex) => (
                <TableRow key={fieldIndex}>
                  <TableCell align="left"></TableCell>
                  <TableCell align="left">{field.name}</TableCell>
                  <TableCell align="left">
                    {field.previous_value || '-'}
                  </TableCell>
                  <TableCell align="left">{field.value}</TableCell>
                </TableRow>
              ),
            )}
          </TableBody>
        </StyledTable>
      </>
    </>
  );
};
