import React, { useState } from 'react';
import styled from 'styled-components';
import { Button, Grid, Typography } from '@material-ui/core';
import { Missing } from '../../Missing';
import { DashboardPaper } from '../DashboardPaper';
import { GrievancesChart } from '../charts/GrievancesChart';

const CardTitleSmaller = styled.div`
  text-transform: capitalize;
  color: #6f6f6f;
  font-weight: 500;
  font-size: 11px;
`;

export const GrievancesSection = (): React.ReactElement => {
  const [show, setShow] = useState(false);
  return (
    <DashboardPaper title='Grievances'>
      <CardTitleSmaller>TOTAL NUMBER OF GRIEVANCES</CardTitleSmaller>
      <Typography variant='caption'>
        1,2345 <Missing />
      </Typography>
      <GrievancesChart />
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <CardTitleSmaller>NUMBER OF DATA CHANGE GRIEVANCES</CardTitleSmaller>
          <Typography variant='caption'>
            1,2345 <Missing />
          </Typography>
        </Grid>
      </Grid>
      {show ? (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <CardTitleSmaller>NUMBER OF SENSITIVE GRIEVANCES</CardTitleSmaller>
            <Typography variant='caption'>
              1,2345 <Missing />
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <CardTitleSmaller>
              NUMBER OF GRIEVANCE COMPLAINT GRIEVANCES
            </CardTitleSmaller>
            <Typography variant='caption'>
              1,2345 <Missing />
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <CardTitleSmaller>
              NUMBER OF NEGATIVE FEEDBACK GRIEVANCES
            </CardTitleSmaller>
            <Typography variant='caption'>
              1,2345 <Missing />
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <CardTitleSmaller>NUMBER OF REFERRAL GRIEVANCES</CardTitleSmaller>
            <Typography variant='caption'>
              1,2345 <Missing />
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <CardTitleSmaller>
              NUMBER OF POSITIVE FEEDBACK GRIEVANCES
            </CardTitleSmaller>
            <Typography variant='caption'>
              1,2345 <Missing />
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
