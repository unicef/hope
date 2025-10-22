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
import PhotoModal from '@components/core/PhotoModal/PhotoModal';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';

const StyledTable = styled(Table)`
  color: #9e9e9e;
`;

const GreenIcon = styled.div`
  color: #28cb15;
`;

export interface DocumentsTableProps {
  values;
  isEdit;
  ticket: GrievanceTicketDetail;
  documents;
  setFieldValue;
  documentTypeDict;
  countriesDict;
}

export function DocumentsTable({
  values,
  isEdit,
  ticket,
  setFieldValue,
  documents,
  documentTypeDict,
  countriesDict,
}: DocumentsTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedDocuments } = values;
  const handleSelectDocument = (documentIndex): void => {
    handleSelected(
      documentIndex,
      'selectedDocuments',
      selectedDocuments,
      setFieldValue,
    );
  };
  const documentsTableHead = (
    <TableHead>
      <TableRow>
        <TableCell align="left" />
        <TableCell data-cy="table-cell-id-type" align="left">
          {t('ID Type')}
        </TableCell>
        <TableCell data-cy="table-cell-country" align="left">
          {t('Country')}
        </TableCell>
        <TableCell data-cy="table-cell-number" align="left">
          {t('Number')}
        </TableCell>
        <TableCell data-cy="table-cell-photo" align="left">
          {t('Photo')}
        </TableCell>
      </TableRow>
    </TableHead>
  );
  return (
    <>
      <TableTitle>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">{t('Documents to be added')}</Typography>
        </Box>
      </TableTitle>
      <StyledTable>
        {documentsTableHead}
        <TableBody>
          {documents?.map((row, index) => (
            <TableRow key={`${row.value.type}-${row.value.country}`}>
              <TableCell align="left">
                {isEdit ? (
                  <Checkbox
                    color="primary"
                    data-cy="checkbox-document"
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
                    <GreenIcon data-cy="green-check-icon">
                      <CheckCircleIcon />
                    </GreenIcon>
                  )
                )}
              </TableCell>
              <TableCell align="left">
                {documentTypeDict[row.value.key]}
              </TableCell>
              <TableCell align="left">
                {countriesDict[row.value.country]}
              </TableCell>
              <TableCell align="left">{row.value.number}</TableCell>
              <TableCell align="left">
                {row.value.photo ? <PhotoModal src={row.value.photo} /> : '-'}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </StyledTable>
    </>
  );
}
