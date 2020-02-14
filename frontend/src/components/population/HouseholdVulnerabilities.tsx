import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: 20px;
  &:first-child {
    margin-top: 0px;
  }
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function HouseholdVulnerabilities(): React.ReactElement {
  return (
    <div>
      <Overview>
        <Title>
          <Typography variant='h6'>Vulnerabilities</Typography>
        </Title>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='Living Situation'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Construction Material'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Shelter Quality'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Number of Rooms'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Total Dweller'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Dwellers in one room'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Total Households'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Source of water'>
              <div> </div>
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
      <Overview>
        <Title>
          <Typography variant='h6'>Registration Details</Typography>
        </Title>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='Source'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Intake group name'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Registered Date'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Number of Rooms'>
              <div> </div>
            </LabelizedField>
          </Grid>
        </Grid>
        <hr />
        <Typography variant='h6'>Data Collection</Typography>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='Start time'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='End time'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Device ID'>
              <div> </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='User name'>
              <div> </div>
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </div>
  );
}
