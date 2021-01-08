import { Grid } from '@material-ui/core';
import React from 'react';
import PeopleIcon from '@material-ui/icons/People';
import {
  CardAmountSmaller,
  CardTitle,
  DashboardCard,
  IconContainer,
} from '../DashboardCard';

export const TotalNumberOfHouseholdsReachedSection = (): React.ReactElement => {
  return (
    <DashboardCard color='#00A9FB'>
      <CardTitle>TOTAL NUMBER OF HOUSEHOLDS REACHED</CardTitle>
      <Grid container justify='space-between' alignItems='center'>
        <Grid item>
          <CardAmountSmaller>32634245</CardAmountSmaller>
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
