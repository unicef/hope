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

export interface IdentitiesTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketNode;
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
        <TableCell align='left'>{t('Agency')}</TableCell>
        <TableCell align='left'>{t('Country')}</TableCell>
        <TableCell align='left'>{t('Number')}</TableCell>
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
              <TableRow key={`${row.value.agency}-${row.value.agency}`}>
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
                    />
                  ) : (
                    selectedIdentities.includes(index) && (
                      <GreenIcon>
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </TableCell>
                <TableCell align='left'>
                  {identityTypeDict[row.value.agency]}
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
