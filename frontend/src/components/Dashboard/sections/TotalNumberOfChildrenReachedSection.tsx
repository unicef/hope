import { Grid } from '@material-ui/core';
import React from 'react';
import ChildCareIcon from '@material-ui/icons/ChildCare';
import {
  CardAmountSmaller,
  CardTitle,
  DashboardCard,
  IconContainer,
} from '../DashboardCard';

export const TotalNumberOfChildrenReachedSection = (): React.ReactElement => {
  return (
    <DashboardCard color='#4CD0E0'>
      <CardTitle>TOTAL NUMBER OF CHILDREN REACHED</CardTitle>
      <Grid container justify='space-between' alignItems='center'>
        <Grid item>
          <CardAmountSmaller>85234657</CardAmountSmaller>
        </Grid>
        <Grid item>
          <IconContainer bg='#E4F7FA' color='#4CD0E0'>
            <ChildCareIcon fontSize='inherit' />
          </IconContainer>
        </Grid>
      </Grid>
    </DashboardCard>
  );
};
