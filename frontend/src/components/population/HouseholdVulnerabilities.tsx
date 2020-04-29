import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import {Missing} from "../Missing";

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
              <Missing/>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Construction Material'>
              <Missing/>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Shelter Quality'>
              <Missing/>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Number of Rooms'>
              <Missing/>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Total Dweller'>
              <Missing/>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Dwellers in one room'>
              <Missing/>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Total Households'>
              <Missing/>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Source of water'>
              <Missing/>
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </div>
  );
}
