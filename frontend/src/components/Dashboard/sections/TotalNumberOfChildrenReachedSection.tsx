import { Grid } from '@material-ui/core';
import React from 'react';
import ChildCareIcon from '@material-ui/icons/ChildCare';
import {
  CardAmountSmaller,
  CardTitle,
  DashboardCard,
  IconContainer,
} from '../DashboardCard';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface TotalNumberOfChildrenReachedSectionProps {
  data: AllChartsQuery['sectionChildReached'];
}

export const TotalNumberOfChildrenReachedSection = ({
  data,
}: TotalNumberOfChildrenReachedSectionProps): React.ReactElement => {
  return (
    <DashboardCard color='#4CD0E0'>
      <CardTitle>TOTAL NUMBER OF CHILDREN REACHED</CardTitle>
      <Grid container justify='space-between' alignItems='center'>
        <Grid item>
          <CardAmountSmaller>{data?.total}</CardAmountSmaller>
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
