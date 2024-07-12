import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import {
  Typography,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell as MuiTableCell,
  TableBody,
  TableCell,
} from '@mui/material';
import styled from 'styled-components';
import { Title } from '@core/Title';
import { useTranslation } from 'react-i18next';

const StyledTableCell = styled(MuiTableCell)`
  color: #adadad !important;
`;

//TODO MS: add proper type
interface ProgrammeTimeSeriesFieldsProps {
  program?: any;
}

export const ProgrammeTimeSeriesFields = ({
  program,
}: ProgrammeTimeSeriesFieldsProps): React.ReactElement => {
  const { t } = useTranslation();
  // TODO MS: remove
  console.log(program);

  // Example data structure for the table rows
  // Replace or modify according to your actual data source
  const rows = [
    {
      fieldName: 'Example Field 1',
      roundNumber: 1,
      roundName: 'Round 1',
      value: 'Value 1',
      dateOfCollection: '2023-01-01',
    },
    {
      fieldName: 'Example Field 2',
      roundNumber: 2,
      roundName: 'Round 2',
      value: 'Value 2',
      dateOfCollection: '2023-02-01',
    },
    // Add more rows as needed
  ];

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
            {rows.map((row, index) => (
              <TableRow key={index}>
                <TableCell component="th" scope="row">
                  {row.fieldName}
                </TableCell>
                <TableCell align="right">{row.roundNumber}</TableCell>
                <TableCell align="left">{row.roundName}</TableCell>
                <TableCell align="left">{row.value}</TableCell>
                <TableCell align="right">{row.dateOfCollection}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </ContainerColumnWithBorder>
  );
};
