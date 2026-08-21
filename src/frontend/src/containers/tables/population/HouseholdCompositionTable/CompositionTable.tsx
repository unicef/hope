import { LabelizedField } from '@components/core/LabelizedField';
import { Title } from '@components/core/Title';
import { Info } from '@mui/icons-material';
import {
  Box,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const GreyTableCell = styled(TableCell)`
  background-color: #eeeeee;
`;
const OverviewPaper = styled(Paper)`
  margin: 20px 20px 0 20px;
  padding: 20px ${({ theme }) => theme.spacing(11)};
`;

type Count = number | null | undefined;

export interface CompositionRow {
  ageGroup: string;
  female: Count;
  femaleDisabled: Count;
  pregnant?: Count;
  male: Count;
  maleDisabled: Count;
  dataCy?: string;
}

export interface CompositionTableProps {
  title: string;
  tooltip?: string;
  rows: CompositionRow[];
  footer: { label: string; value: Count; dataCy?: string }[];
  dataCy?: string;
}

// null means "not collected", 0 is a real zero - never collapse the two
const format = (value: Count): string =>
  value === null || value === undefined ? '-' : String(value);

export function CompositionTable({
  title,
  tooltip,
  rows,
  footer,
  dataCy,
}: CompositionTableProps): ReactElement {
  const { t } = useTranslation();
  return (
    <OverviewPaper data-cy={dataCy}>
      <Title>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="h6">{title}</Typography>
          {tooltip && (
            <Tooltip title={tooltip}>
              <IconButton
                color="primary"
                aria-label={title}
                data-cy="composition-table-info"
              >
                <Info />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </Title>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell align="left">{t('Age Group')}</TableCell>
            <GreyTableCell align="left">{t('Females')}</GreyTableCell>
            <GreyTableCell align="left">{t('with disability')}</GreyTableCell>
            <GreyTableCell align="left">{t('Pregnant')}</GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">{t('Males')}</GreyTableCell>
            <GreyTableCell align="left">{t('with disability')}</GreyTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.ageGroup} data-cy={row.dataCy}>
              <TableCell align="left">{row.ageGroup}</TableCell>
              <GreyTableCell align="left">{format(row.female)}</GreyTableCell>
              <GreyTableCell align="left">
                {format(row.femaleDisabled)}
              </GreyTableCell>
              <GreyTableCell align="left">
                {format(row.pregnant)}
              </GreyTableCell>
              <TableCell align="left" />
              <GreyTableCell align="left">{format(row.male)}</GreyTableCell>
              <GreyTableCell align="left">
                {format(row.maleDisabled)}
              </GreyTableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Box
        sx={{
          display: 'flex',
          mt: 2,
        }}
      >
        {footer.map((field) => (
          <Box key={field.label} sx={{ mr: 2 }} data-cy={field.dataCy}>
            <LabelizedField label={field.label} value={format(field.value)} />
          </Box>
        ))}
      </Box>
    </OverviewPaper>
  );
}
