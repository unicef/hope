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

const GreenIcon = styled.div`
  color: #28cb15;
`;
const GreyText = styled.div`
  color: #9e9e9e;
`;

const StyledTable = styled(Table)`
  min-width: 100px;
`;

const Title = styled.div`
  padding-top: ${({ theme }) => theme.spacing(4)}px;
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

export interface IdentitiesToEditTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  countriesDict;
  index;
  identity;
}

export const IdentitiesToEditTable = ({
  values,
  isEdit,
  ticket,
  setFieldValue,
  countriesDict,
  index,
  identity,
}: IdentitiesToEditTableProps) => {
  const { t } = useTranslation();
  const { selectedIdentitiesToEdit } = values;
  const renderNewOrNotUpdated = (prev, curr): React.ReactElement => {
    if (prev === curr) {
      return <GreyText>{t('Not updated')}</GreyText>;
    }
    return <span>{curr}</span>;
  };
  const handleSelectIdentityToEdit = (documentIndex): void => {
    const newSelected = [...selectedIdentitiesToEdit];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedIdentitiesToEdit', newSelected);
  };

  return (
    <>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Identity to be edited')}</Typography>
        </Box>
      </Title>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align='left'>
              {isEdit ? (
                <Checkbox
                  color='primary'
                  onChange={(): void => {
                    handleSelectIdentityToEdit(index);
                  }}
                  disabled={
                    ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                  }
                  checked={selectedIdentitiesToEdit.includes(index)}
                  inputProps={{ 'aria-labelledby': 'selected' }}
                />
              ) : (
                selectedIdentitiesToEdit.includes(index) && (
                  <GreenIcon>
                    <CheckCircleIcon />
                  </GreenIcon>
                )
              )}
            </TableCell>
            <TableCell align='left'>{t('Field')}</TableCell>
            <TableCell align='left'>{t('Current Value')}</TableCell>
            <TableCell align='left'>{t('New Value')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell />
            <TableCell align='left'>{t('Agency')}</TableCell>
            <TableCell align='left'>{identity.previous_value.agency}</TableCell>
            <TableCell align='left'>
              {identity.value?.agency ?? (
                <GreyText>{t('Not updated')}</GreyText>
              )}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align='left'>{t('Country')}</TableCell>
            <TableCell align='left'>
              {countriesDict[identity.previous_value.country]}
            </TableCell>
            <TableCell align='left'>
              {renderNewOrNotUpdated(
                countriesDict[identity.previous_value.country],
                countriesDict[identity.value?.country],
              )}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell />
            <TableCell align='left'>{t('Identity Number')}</TableCell>
            <TableCell align='left'>{identity.previous_value.number}</TableCell>
            <TableCell align='left'>
              {renderNewOrNotUpdated(
                identity.previous_value.number,
                identity.value?.number,
              )}
            </TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </>
  );
};
