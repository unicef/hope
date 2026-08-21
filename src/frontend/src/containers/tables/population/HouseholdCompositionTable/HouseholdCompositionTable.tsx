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
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
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

export interface HouseholdCompositionTableProps {
  household: HouseholdDetail;
}

type Count = number | null | undefined;

// null means "not collected", 0 is a real zero - never collapse the two
const format = (value: Count): string =>
  value === null || value === undefined ? '-' : String(value);

export function HouseholdCompositionTable({
  household,
}: HouseholdCompositionTableProps): ReactElement {
  const { t } = useTranslation();
  const rows: {
    ageGroup: string;
    female: Count;
    femaleDisabled: Count;
    pregnant?: Count;
    male: Count;
    maleDisabled: Count;
    dataCy?: string;
  }[] = [
    {
      ageGroup: '0 - 5',
      dataCy: 'row05',
      female: household?.kabFemaleAgeGroup05Count,
      femaleDisabled: household?.kabFemaleAgeGroup05DisabledCount,
      male: household?.kabMaleAgeGroup05Count,
      maleDisabled: household?.kabMaleAgeGroup05DisabledCount,
    },
    {
      ageGroup: '6 - 11',
      female: household?.kabFemaleAgeGroup611Count,
      femaleDisabled: household?.kabFemaleAgeGroup611DisabledCount,
      male: household?.kabMaleAgeGroup611Count,
      maleDisabled: household?.kabMaleAgeGroup611DisabledCount,
    },
    {
      ageGroup: '12 - 17',
      female: household?.kabFemaleAgeGroup1217Count,
      femaleDisabled: household?.kabFemaleAgeGroup1217DisabledCount,
      male: household?.kabMaleAgeGroup1217Count,
      maleDisabled: household?.kabMaleAgeGroup1217DisabledCount,
    },
    {
      ageGroup: '18 - 59',
      female: household?.kabFemaleAgeGroup1859Count,
      femaleDisabled: household?.kabFemaleAgeGroup1859DisabledCount,
      pregnant: household?.kabPregnantCount,
      male: household?.kabMaleAgeGroup1859Count,
      maleDisabled: household?.kabMaleAgeGroup1859DisabledCount,
    },
    {
      ageGroup: '60 +',
      female: household?.kabFemaleAgeGroup60Count,
      femaleDisabled: household?.kabFemaleAgeGroup60DisabledCount,
      male: household?.kabMaleAgeGroup60Count,
      maleDisabled: household?.kabMaleAgeGroup60DisabledCount,
    },
  ];
  const footer = [
    {
      label: t('Other'),
      value: household?.kabOtherSexGroupCount,
      dataCy: 'kab-other',
    },
    {
      label: t('Unknown'),
      value: household?.kabUnknownSexGroupCount,
      dataCy: 'kab-unknown',
    },
    { label: t('Size'), value: household?.kabSize, dataCy: 'kab-size' },
  ];
  return (
    <OverviewPaper data-cy="known-affected-beneficiaries">
      <Title>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="h6">
            {t('Known Affected Beneficiaries')}
          </Typography>
          <Tooltip
            title={t(
              'Figures represent known affected beneficiaries counted from individual records, not declared household size.',
            )}
          >
            <IconButton
              color="primary"
              aria-label={t('Known Affected Beneficiaries')}
              data-cy="composition-table-info"
            >
              <Info />
            </IconButton>
          </Tooltip>
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
              <GreyTableCell align="left">{format(row.pregnant)}</GreyTableCell>
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
