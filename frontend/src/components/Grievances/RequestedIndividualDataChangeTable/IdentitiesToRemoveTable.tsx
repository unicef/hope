import React from 'react';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { useTranslation } from 'react-i18next';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import styled from 'styled-components';
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
import { GRIEVANCE_TICKET_STATES } from '../../../utils/constants';

const GreenIcon = styled.div`
  color: #28cb15;
`;
const StyledTable = styled(Table)`
  min-width: 100px;
`;
const Title = styled.div`
  padding-top: ${({ theme }) => theme.spacing(4)}px;
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

export interface IdentitiesToRemoveTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  countriesDict;
  identitiesToRemove;
  previousIdentities;
}

export const IdentitiesToRemoveTable = ({
  values,
  isEdit,
  ticket,
  countriesDict,
  identitiesToRemove,
  previousIdentities,
  setFieldValue,
}: IdentitiesToRemoveTableProps) => {
  const { t } = useTranslation();
  const { selectedIdentitiesToRemove } = values;
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
  const handleSelectIdentityToRemove = (identityIndex): void => {
    const newSelected = [...selectedIdentitiesToRemove];
    const selectedIndex = newSelected.indexOf(identityIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(identityIndex);
    }
    setFieldValue('selectedIdentitiesToRemove', newSelected);
  };

  return (
    <>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Identities to be removed')}</Typography>
        </Box>
      </Title>
      <StyledTable>
        {identitiesTableHead}
        <TableBody>
          {identitiesToRemove?.map((row, index) => {
            const identity = previousIdentities[row.value];
            return (
              <TableRow key={`${identity.label}-${identity.country}`}>
                <TableCell align='left'>
                  {isEdit ? (
                    <Checkbox
                      onChange={(): void => {
                        handleSelectIdentityToRemove(index);
                      }}
                      color='primary'
                      disabled={
                        ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                      }
                      checked={selectedIdentitiesToRemove.includes(index)}
                      inputProps={{ 'aria-labelledby': 'xd' }}
                    />
                  ) : (
                    selectedIdentitiesToRemove.includes(index) && (
                      <GreenIcon>
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </TableCell>
                <TableCell align='left'>{identity?.label || '-'}</TableCell>
                <TableCell align='left'>
                  {countriesDict[identity?.country] || '-'}
                </TableCell>
                <TableCell align='left'>{identity?.number || '-'}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </StyledTable>
    </>
  );
};
