import React from 'react';
import styled from 'styled-components';
import {Grid, Typography} from '@material-ui/core';
import {DashboardPaper} from '../DashboardPaper';
import {GrievancesChart} from '../charts/GrievancesChart';
import {AllChartsQuery} from '../../../__generated__/graphql';
import {formatNumber} from '../../../utils/utils';

const CardTitleSmaller = styled.div`
  text-transform: capitalize;
  color: #6f6f6f;
  font-weight: 500;
  font-size: 11px;
`;

interface GrievancesSectionProps {
  data: AllChartsQuery['chartGrievances'];
}

export const GrievancesSection = ({
  data,
}: GrievancesSectionProps): React.ReactElement => {
  if (!data) return null;
  return (
    <DashboardPaper title='Grievances and Feedback'>
      <Grid container spacing={3}>
        <Grid item xs={6}>
          <CardTitleSmaller>TOTAL NUMBER OF GRIEVANCES</CardTitleSmaller>
          <Typography variant='caption'>
            {formatNumber(data?.totalNumberOfGrievances)}
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <CardTitleSmaller>TOTAL NUMBER OF FEEDBACK</CardTitleSmaller>
          <Typography variant='caption'>
            {formatNumber(data?.totalNumberOfFeedback)}
          </Typography>
        </Grid>
      </Grid>
      <GrievancesChart data={data} />
      <CardTitleSmaller>NUMBER OF OPEN SENSITIVE GRIEVANCES</CardTitleSmaller>
      <Typography variant='caption'>
        {formatNumber(data?.totalNumberOfOpenSensitive)}
      </Typography>
    </DashboardPaper>
  );
};
