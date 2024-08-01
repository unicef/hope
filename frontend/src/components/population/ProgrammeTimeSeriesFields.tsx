import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import {
  TableCell as MuiTableCell,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const StyledTableCell = styled(MuiTableCell)`
  color: #adadad !important;
`;

//TODO MS: add proper type
interface ProgrammeTimeSeriesFieldsProps {
  periodicFieldsData: any;
}

export const ProgrammeTimeSeriesFields = ({
  periodicFieldsData,
}: ProgrammeTimeSeriesFieldsProps): React.ReactElement => {
  const { t } = useTranslation();

  const rows = periodicFieldsData?.results || [];

  //TODO MS: add missing fields
  const mappedRows = rows.flatMap((row) =>
    (row.pdu_data?.rounds_names || []).map((roundName, index) => ({
      fieldName: row.name,
      roundNumber: index + 1,
      roundName: roundName,
      value: null, // Assuming value is not available in the provided data
      dateOfCollection: null, // Assuming dateOfCollection is not available in the provided data
    })),
  );

  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">
          {t('Programme Time Series Fields')}
        </Typography>
      </Title>
      <TableContainer component={'div'} style={{ backgroundColor: '#f5f5f5' }}>
        <Table aria-label="programme time series fields">
          <TableHead>
            <TableRow>
              <StyledTableCell>{t('Field Name')}</StyledTableCell>
              <StyledTableCell align="right">
                {t('Round Number')}
              </StyledTableCell>
              <StyledTableCell align="left">{t('Round Name')}</StyledTableCell>
              <StyledTableCell align="left">{t('Value')}</StyledTableCell>
              <StyledTableCell align="right">
                {t('Date of Collection')}
              </StyledTableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mappedRows.map((row, index) => (
              <TableRow key={`${row.fieldName}-${row.roundNumber}-${index}`}>
                <TableCell component="th" scope="row">
                  {row.fieldName}
                </TableCell>
                <TableCell align="right">{row.roundNumber}</TableCell>
                <TableCell align="left">{row.roundName}</TableCell>
                <TableCell align="left">{row.value}</TableCell>
                <TableCell align="right">
                  <UniversalMoment>{row.dateOfCollection}</UniversalMoment>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </ContainerColumnWithBorder>
  );
};
