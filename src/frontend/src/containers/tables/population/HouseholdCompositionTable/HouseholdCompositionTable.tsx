import { Title } from '@components/core/Title';
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
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
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

export function HouseholdCompositionTable({
  household,
}: HouseholdCompositionTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiary_group;
  return (
    <OverviewPaper>
      <Title>
        <Typography variant="h6">{`${beneficiaryGroup?.group_label} Composition`}</Typography>
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
              {household?.female_age_group_0_5_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.female_age_group_0_5_disabled_count}
            </GreyTableCell>
            <GreyTableCell align="left">-</GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.male_age_group_0_5_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.male_age_group_0_5_disabled_count}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align="left">6 - 11</TableCell>
            <GreyTableCell align="left">
              {household?.female_age_group_6_11_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.female_age_group_6_11_disabled_count}
            </GreyTableCell>
            <GreyTableCell align="left">-</GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.male_age_group_6_11_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.male_age_group_6_11_disabled_count}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align="left">12 - 17</TableCell>
            <GreyTableCell align="left">
              {household?.female_age_group_12_17_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.female_age_group_12_17_disabled_count}
            </GreyTableCell>
            <GreyTableCell align="left">-</GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.male_age_group_12_17_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.male_age_group_12_17_disabled_count}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align="left">18 - 59</TableCell>
            <GreyTableCell align="left">
              {household?.female_age_group_18_59_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.female_age_group_18_59_disabled_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.pregnant_count}
            </GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.male_age_group_18_59_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.male_age_group_18_59_disabled_count}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align="left">60 +</TableCell>
            <GreyTableCell align="left">
              {household?.female_age_group_60_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.female_age_group_60_disabled_count}
            </GreyTableCell>
            <GreyTableCell align="left">-</GreyTableCell>
            <TableCell align="left" />
            <GreyTableCell align="left">
              {household?.male_age_group_60_count}
            </GreyTableCell>
            <GreyTableCell align="left">
              {household?.male_age_group_60_disabled_count}
            </GreyTableCell>
          </TableRow>
        </TableBody>
      </Table>
      <Box display="flex" mt={2}>
        {/* TODO: Add the following fields */}
        <Box mr={2}>
          {/* <LabelizedField
            label={t('Unknown')}
            value={household?.count}
          /> */}
        </Box>
        <Box>
          {/* <LabelizedField
            label={t('Other')}
            value={household?.otherSexGroupCount}
          /> */}
        </Box>
      </Box>
    </OverviewPaper>
  );
}
