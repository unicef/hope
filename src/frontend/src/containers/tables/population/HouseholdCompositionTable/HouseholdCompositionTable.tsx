import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Title } from '@components/core/Title';
import { HouseholdNode } from '@generated/graphql';
import { useProgramContext } from 'src/programContext';
import { LabelizedField } from '@components/core/LabelizedField';

const GreyTableCell = styled(TableCell)`
  background-color: #eeeeee;
`;
const OverviewPaper = styled(Paper)`
  margin: 20px 20px 0 20px;
  padding: 20px ${({ theme }) => theme.spacing(11)};
`;
export interface HouseholdCompositionTableProps {
  household: HouseholdNode;
}

export function HouseholdCompositionTable({
  household,
}: HouseholdCompositionTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  return (
    <OverviewPaper>
      <Title>
        <Typography variant="h6">{`${beneficiaryGroup?.groupLabel} Composition`}</Typography>
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
          <TableRow data-cy="row05">
            <TableCell align="left">0 - 5</TableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup05Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup05DisabledCount}
            </GreyTableCell>
            <GreyTableCell align="left">-</GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.maleAgeGroup05Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.maleAgeGroup05DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align="left">6 - 11</TableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup611Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup611DisabledCount}
            </GreyTableCell>
            <GreyTableCell align="left">-</GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.maleAgeGroup611Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.maleAgeGroup611DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align="left">12 - 17</TableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup1217Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup1217DisabledCount}
            </GreyTableCell>
            <GreyTableCell align="left">-</GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.maleAgeGroup1217Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.maleAgeGroup1217DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align="left">18 - 59</TableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup1859Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup1859DisabledCount}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.pregnantCount}
            </GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.maleAgeGroup1859Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.maleAgeGroup1859DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align="left">60 +</TableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup60Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.femaleAgeGroup60DisabledCount}
            </GreyTableCell>
            <GreyTableCell align="left">-</GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.maleAgeGroup60Count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.maleAgeGroup60DisabledCount}
            </GreyTableCell>
          </TableRow>
        </TableBody>
      </Table>
      <Box display="flex" mt={2}>
        <Box mr={2}>
          <LabelizedField
            label={t('Unknown')}
            value={household?.unknownSexGroupCount}
          />
        </Box>
        <Box>
          <LabelizedField
            label={t('Other')}
            value={household?.otherSexGroupCount}
          />
        </Box>
      </Box>
    </OverviewPaper>
  );
}
