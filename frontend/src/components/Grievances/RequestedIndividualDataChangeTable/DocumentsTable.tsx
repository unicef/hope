import {
  Box,
  Typography,
  Table,
  TableBody,
  TableRow,
  TableCell,
  Checkbox,
  TableHead,
} from '@material-ui/core';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { GRIEVANCE_TICKET_STATES } from '../../../utils/constants';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';

const Title = styled.div`
  padding-top: ${({ theme }) => theme.spacing(4)}px;
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

const StyledTable = styled(Table)`
  color: #9e9e9e;
`;

const GreenIcon = styled.div`
  color: #28cb15;
`;

export interface DocumentsTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  documents;
  setFieldValue;
  documentTypeDict;
  countriesDict;
}

export const DocumentsTable = ({
  values,
  isEdit,
  ticket,
  setFieldValue,
  documents,
  documentTypeDict,
  countriesDict,
}: DocumentsTableProps) => {
  const { t } = useTranslation();
  const { selectedDocuments } = values;
  const handleSelectDocument = (documentIndex): void => {
    const newSelected = [...selectedDocuments];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedDocuments', newSelected);
  };
  const documentsTableHead = (
    <TableHead>
      <TableRow>
        <TableCell align='left' />
        <TableCell align='left'>{t('ID Type')}</TableCell>
        <TableCell align='left'>{t('Country')}</TableCell>
        <TableCell align='left'>{t('Number')}</TableCell>
      </TableRow>
    </TableHead>
  );
  return (
    <>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Documents to be added')}</Typography>
        </Box>
      </Title>
      <StyledTable>
        {documentsTableHead}
        <TableBody>
          {documents?.map((row, index) => {
            return (
              <TableRow key={`${row.value.type}-${row.value.country}`}>
                <TableCell align='left'>
                  {isEdit ? (
                    <Checkbox
                      color='primary'
                      onChange={(): void => {
                        handleSelectDocument(index);
                      }}
                      disabled={
                        ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                      }
                      checked={selectedDocuments.includes(index)}
                      inputProps={{ 'aria-labelledby': 'selected' }}
                    />
                  ) : (
                    selectedDocuments.includes(index) && (
                      <GreenIcon>
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </TableCell>
                <TableCell align='left'>
                  {documentTypeDict[row.value.type]}
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
