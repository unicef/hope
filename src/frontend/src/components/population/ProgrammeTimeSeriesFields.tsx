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
  Box,
} from '@mui/material';
import styled from 'styled-components';
import { Title } from '@core/Title';
import { useTranslation } from 'react-i18next';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { IndividualNode } from '@generated/graphql';
import { UniversalMoment } from '@core/UniversalMoment';

const StyledTableCell = styled(MuiTableCell)`
  color: #adadad !important;
`;

//TODO MS: add proper type
interface ProgrammeTimeSeriesFieldsProps {
  individual: IndividualNode;
  periodicFieldsData: any;
}

export const ProgrammeTimeSeriesFields = ({
  individual,
  periodicFieldsData,
}: ProgrammeTimeSeriesFieldsProps): React.ReactElement => {
  const { t } = useTranslation();
  const pduDataDict = useArrayToDict(
    periodicFieldsData?.results || [],
    'name',
    '*',
  );
  const rows = [];
  if (individual.flexFields && Object.keys(individual.flexFields).length > 0) {
    for (const fieldName of Object.keys(individual.flexFields)) {
      if (
        individual.flexFields[fieldName] &&
        Object.keys(individual.flexFields[fieldName]).length > 0
      ) {
        for (const roundNumber of Object.keys(
          individual.flexFields[fieldName],
        )) {
          const roundData = individual.flexFields[fieldName][roundNumber];
          if (
            roundData &&
            pduDataDict[fieldName] &&
            pduDataDict[fieldName].pdu_data.rounds_names
          ) {
            const roundName =
              pduDataDict[fieldName].pdu_data.rounds_names[
                parseInt(roundNumber) - 1
              ];
            const value = roundData.value;
            const dateOfCollection = roundData.collection_date;
            rows.push({
              key: `${pduDataDict[fieldName]}-roundNumber`,
              fieldName: pduDataDict[fieldName].label,
              roundNumber: roundNumber,
              roundName: roundName,
              value,
              dateOfCollection,
            });
          }
        }
      }
    }
  }

  return (
    <Box mb={3}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">
            {t('Programme Time Series Fields')}
          </Typography>
        </Title>
        <TableContainer
          component={'div'}
          style={{ backgroundColor: '#f5f5f5' }}
        >
          <Table aria-label="programme time series fields">
            <TableHead>
              <TableRow>
                <StyledTableCell>{t('Field Name')}</StyledTableCell>
                <StyledTableCell align="right">
                  {t('Round Number')}
                </StyledTableCell>
                <StyledTableCell align="left">
                  {t('Round Name')}
                </StyledTableCell>
                <StyledTableCell align="left">{t('Value')}</StyledTableCell>
                <StyledTableCell align="right">
                  {t('Date of Collection')}
                </StyledTableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.length > 0 ? (
                rows.map((row) => (
                  <TableRow key={row.key}>
                    <TableCell component="th" scope="row">
                      {row.fieldName}
                    </TableCell>
                    <TableCell align="right">{row.roundNumber}</TableCell>
                    <TableCell align="left">{row.roundName}</TableCell>
                    <TableCell align="left">
                      {typeof row.value == 'boolean'
                        ? row.value
                          ? 'YES'
                          : 'NO'
                        : row.value}
                    </TableCell>
                    <TableCell align="right">
                      <UniversalMoment>{row.dateOfCollection}</UniversalMoment>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    {t('No data available')}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </ContainerColumnWithBorder>
    </Box>
  );
};
