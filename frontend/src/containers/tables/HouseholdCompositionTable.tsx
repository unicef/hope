import {Paper, Table, TableBody, TableCell, TableHead, TableRow, Typography,} from '@material-ui/core';
import styled from 'styled-components';
import React, {ReactElement} from 'react';
import {HouseholdDetailedFragment} from '../../__generated__/graphql';

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
  return (
    <OverviewPaper>
      <Title>
        <Typography variant='h6'>Household Composition</Typography>
      </Title>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell align='left'>Age Group</TableCell>
            <GreyTableCell align='left'>Females</GreyTableCell>
            <GreyTableCell align='left'>with disability</GreyTableCell>
            <GreyTableCell align='left'>Pregnant</GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>Males</GreyTableCell>
            <GreyTableCell align='left'>with disability</GreyTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell align='left'>0-5</TableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup05Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup05DisabledCount}
            </GreyTableCell>
            <GreyTableCell align='left'>-</GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>
              {household.maleAgeGroup05Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.maleAgeGroup05DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left'>6-11</TableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup611Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup611DisabledCount}
            </GreyTableCell>
            <GreyTableCell align='left'>-</GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>
              {household.maleAgeGroup611Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.maleAgeGroup611DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left'>12-&lt;17</TableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup1217Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.femaleAgeGroup1217DisabledCount}
            </GreyTableCell>
            <GreyTableCell align='left'>-</GreyTableCell>
            <TableCell align='left' />
            <GreyTableCell align='left'>
              {household.maleAgeGroup1217Count}
            </GreyTableCell>
            <GreyTableCell align='left'>
              {household.maleAgeGroup1217DisabledCount}
            </GreyTableCell>
          </TableRow>
          <TableRow>
            <TableCell align='left'>18-&lt;59</TableCell>
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
            <TableCell align='left'>60+</TableCell>
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
