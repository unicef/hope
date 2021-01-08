import { Grid } from '@material-ui/core';
import React from 'react';
import PersonIcon from '@material-ui/icons/Person';
import {
  CardAmountSmaller,
  CardTitle,
  DashboardCard,
  IconContainer,
} from '../DashboardCard';

export const TotalNumberOfIndividualsReachedSection = (): React.ReactElement => {
  return (
    <DashboardCard color='#345DA0'>
      <CardTitle>TOTAL NUMBER OF INDIVIDUALS REACHED</CardTitle>
      <Grid container justify='space-between' alignItems='center'>
        <Grid item>
          <CardAmountSmaller>169178378</CardAmountSmaller>
        </Grid>
        <Grid item>
          <IconContainer bg='#D9E2EF' color='#023F90'>
            <PersonIcon fontSize='inherit' />
          </IconContainer>
        </Grid>
      </Grid>
    </DashboardCard>
  );
};
