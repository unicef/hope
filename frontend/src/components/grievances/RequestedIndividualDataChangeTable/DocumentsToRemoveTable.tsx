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

export interface DocumentsToRemoveTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketNode;
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
}: DocumentsToRemoveTableProps): React.ReactElement => {
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
    handleSelected(
      documentIndex,
      'selectedDocumentsToRemove',
      selectedDocumentsToRemove,
      setFieldValue,
    );
  };

  return (
    <>
      <TableTitle>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Documents to be removed')}</Typography>
        </Box>
      </TableTitle>
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
