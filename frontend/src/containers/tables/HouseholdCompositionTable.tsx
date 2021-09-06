import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { HouseholdDetailedFragment } from '../../__generated__/graphql';

const GreyTableCell = styled(TableCell)`
  background-color: #eeeeee;
`;
const OverviewPaper = styled(Paper)`
  margin: 20px 20px 0 20px;
  padding: 20px ${({ theme }) => theme.spacing(11)}px;
`;
const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export interface HouseholdCompositionTableProps {
  household: HouseholdDetailedFragment;
}

export function HouseholdCompositionTable({
  household,
}: HouseholdCompositionTableProps): ReactElement {
  const { t } = useTranslation();
  return (
    <OverviewPaper>
      <Title>
        <Typography variant='h6'>{t('Household Composition')}</Typography>
      </Title>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell align='left'>{t('Age Group')}</TableCell>
            <GreyTableCell align='left'>{t('Females')}</GreyTableCell>
            <GreyTableCell align='left'>{t('with disability')}</GreyTableCell>
            <GreyTableCell align='left'>{t('Pregnant')}</GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>{t('Males')}</GreyTableCell>
            <GreyTableCell align='left'>{t('with disability')}</GreyTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell align='left'>0 - 4</TableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup04Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup04DisabledCount}
            </GreyTableCell>
            <GreyTableCell align='left'>-</GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>
              {household.maleAgeGroup04Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.maleAgeGroup04DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left'>5 - 12</TableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup512Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup512DisabledCount}
            </GreyTableCell>
            <GreyTableCell align='left'>-</GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>
              {household.maleAgeGroup512Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.maleAgeGroup512DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left'>13 - 17</TableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup1317Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup1317DisabledCount}
            </GreyTableCell>
            <GreyTableCell align='left'>-</GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>
              {household.maleAgeGroup1317Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.maleAgeGroup1317DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left'>18 - 59</TableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup1859Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup1859DisabledCount}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.pregnantCount}
            </GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>
              {household.maleAgeGroup1859Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.maleAgeGroup1859DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left'>60 +</TableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup60Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup60DisabledCount}
            </GreyTableCell>
            <GreyTableCell align='left'>-</GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>
              {household.maleAgeGroup60Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.maleAgeGroup60DisabledCount}
            </GreyTableCell>
          </TableRow>
        </TableBody>
      </Table>
    </OverviewPaper>
  );
}
