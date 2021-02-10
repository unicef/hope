import React, { useState } from 'react';
import styled from 'styled-components';
import { Button, Grid, Typography } from '@material-ui/core';
import { DashboardPaper } from '../DashboardPaper';
import { GrievancesChart } from '../charts/GrievancesChart';
import { AllChartsQuery } from '../../../__generated__/graphql';

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
  const [show, setShow] = useState(false);
  if (!data) return null;
  return (
    <DashboardPaper title='Grievances'>
      <CardTitleSmaller>TOTAL NUMBER OF GRIEVANCES</CardTitleSmaller>
      <Typography variant='caption'>{data?.total}</Typography>
      <GrievancesChart data={data} />
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <CardTitleSmaller>NUMBER OF DATA CHANGE GRIEVANCES</CardTitleSmaller>
          <Typography variant='caption'>{data?.totalDataChange}</Typography>
        </Grid>
      </Grid>
      {show ? (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <CardTitleSmaller>NUMBER OF SENSITIVE GRIEVANCES</CardTitleSmaller>
            <Typography variant='caption'>{data?.totalSensitive}</Typography>
          </Grid>
          <Grid item xs={12}>
            <CardTitleSmaller>
              NUMBER OF GRIEVANCE COMPLAINT GRIEVANCES
            </CardTitleSmaller>
            <Typography variant='caption'>{data?.totalComplaint}</Typography>
          </Grid>
          <Grid item xs={12}>
            <CardTitleSmaller>
              NUMBER OF NEGATIVE FEEDBACK GRIEVANCES
            </CardTitleSmaller>
            <Typography variant='caption'>
              {data?.totalNegativeFeedback}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <CardTitleSmaller>NUMBER OF REFERRAL GRIEVANCES</CardTitleSmaller>
            <Typography variant='caption'>{data?.totalReferral}</Typography>
          </Grid>
          <Grid item xs={12}>
            <CardTitleSmaller>
              NUMBER OF POSITIVE FEEDBACK GRIEVANCES
            </CardTitleSmaller>
            <Typography variant='caption'>
              {data?.totalPositiveFeedback}
            </Typography>
          </Grid>
        </Grid>
      ) : null}
      <Grid container justify='flex-end'>
        <Button color='primary' onClick={() => setShow(!show)}>
          {show ? 'HIDE' : 'SHOW ALL'}
        </Button>
      </Grid>
    </DashboardPaper>
  );
};
