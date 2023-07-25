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

export interface IdentitiesTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  documentTypeDict;
  countriesDict;
  identityTypeDict;
  document;
  identities;
}

export const IdentitiesTable = ({
  values,
  isEdit,
  ticket,
  setFieldValue,
  countriesDict,
  identityTypeDict,
  identities,
}: IdentitiesTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const { selectedIdentities } = values;

  const handleSelectIdentity = (identityIndex): void => {
    handleSelected(
      identityIndex,
      'selectedIdentities',
      selectedIdentities,
      setFieldValue,
    );
  };
  const identitiesTableHead = (
    <TableHead>
      <TableRow>
        <TableCell align='left' />
        <TableCell data-cy='table-cell-partner' align='left'>
          {t('Partner')}
        </TableCell>
        <TableCell data-cy='table-cell-country' align='left'>
          {t('Country')}
        </TableCell>
        <TableCell data-cy='table-cell-number' align='left'>
          {t('Number')}
        </TableCell>
      </TableRow>
    </TableHead>
  );

  return (
    <>
      <TableTitle>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Identities to be added')}</Typography>
        </Box>
      </TableTitle>
      <StyledTable>
        {identitiesTableHead}
        <TableBody>
          {identities?.map((row, index) => {
            return (
              <TableRow key={`${row.value.partner}-${row.value.partner}`}>
                <TableCell align='left'>
                  {isEdit ? (
                    <Checkbox
                      color='primary'
                      onChange={(): void => {
                        handleSelectIdentity(index);
                      }}
                      disabled={
                        ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                      }
                      checked={selectedIdentities.includes(index)}
                      inputProps={{ 'aria-labelledby': 'selected' }}
                      data-cy='checkbox-identity'
                    />
                  ) : (
                    selectedIdentities.includes(index) && (
                      <GreenIcon data-cy='green-check'>
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </TableCell>
                <TableCell align='left'>
                  {identityTypeDict[row.value.partner]}
                </TableCell>
                <TableCell align='left'>
                  {countriesDict[row.value.country]}
                </TableCell>
                <TableCell align='left'>{row.value.number}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </StyledTable>
    </>
  );
};
