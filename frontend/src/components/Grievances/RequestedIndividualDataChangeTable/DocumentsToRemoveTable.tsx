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
const StyledTable = styled(Table)`
  min-width: 100px;
`;
const Title = styled.div`
  padding-top: ${({ theme }) => theme.spacing(4)}px;
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

export interface DocumentsToRemoveTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  countriesDict;
  documentsToRemove;
  previousDocuments;
}

export const DocumentsToRemoveTable = ({
  values,
  isEdit,
  ticket,
  setFieldValue,
  countriesDict,
  documentsToRemove,
  previousDocuments,
}: DocumentsToRemoveTableProps) => {
  const { t } = useTranslation();
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
  const { selectedDocumentsToRemove } = values;
  const handleSelectDocumentToRemove = (documentIndex): void => {
    const newSelected = [...selectedDocumentsToRemove];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedDocumentsToRemove', newSelected);
  };

  return (
    <>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Documents to be removed')}</Typography>
        </Box>
      </Title>
      <StyledTable>
        {documentsTableHead}
        <TableBody>
          {documentsToRemove?.map((row, index) => {
            const document = previousDocuments[row.value];
            return (
              <TableRow key={`${document.label}-${document.country}`}>
                <TableCell align='left'>
                  {isEdit ? (
                    <Checkbox
                      onChange={(): void => {
                        handleSelectDocumentToRemove(index);
                      }}
                      color='primary'
                      disabled={
                        ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                      }
                      checked={selectedDocumentsToRemove.includes(index)}
                      inputProps={{ 'aria-labelledby': 'xd' }}
                    />
                  ) : (
                    selectedDocumentsToRemove.includes(index) && (
                      <GreenIcon>
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </TableCell>
                <TableCell align='left'>{document?.label || '-'}</TableCell>
                <TableCell align='left'>
                  {countriesDict[document?.country] || '-'}
                </TableCell>
                <TableCell align='left'>
                  {document?.document_number || '-'}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </StyledTable>
    </>
  );
};
