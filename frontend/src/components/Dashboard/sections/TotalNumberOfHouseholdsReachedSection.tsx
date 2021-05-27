import {Grid} from '@material-ui/core';
import React from 'react';
import PeopleIcon from '@material-ui/icons/People';
import {CardAmountSmaller, CardTitle, DashboardCard, IconContainer,} from '../DashboardCard';
import {AllChartsQuery} from '../../../__generated__/graphql';
import {formatNumber} from '../../../utils/utils';

interface TotalNumberOfHouseholdsReachedSectionProps {
  data: AllChartsQuery['sectionHouseholdsReached'];
}

export const TotalNumberOfHouseholdsReachedSection = ({
  data,
}: TotalNumberOfHouseholdsReachedSectionProps): React.ReactElement => {
  if (!data) return null;
  return (
    <DashboardCard color='#00A9FB'>
      <CardTitle>TOTAL NUMBER OF HOUSEHOLDS REACHED</CardTitle>
      <Grid container justify='space-between' alignItems='center'>
        <Grid item>
          <CardAmountSmaller>{formatNumber(data?.total)}</CardAmountSmaller>
        </Grid>
        <Grid item>
          <IconContainer bg='#DAF1FF' color='#00A9FB'>
            <PeopleIcon fontSize='inherit' />
          </IconContainer>
        </Grid>
      </Grid>
    </DashboardCard>
  );
};
