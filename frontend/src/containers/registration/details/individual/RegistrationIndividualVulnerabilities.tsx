import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';
import { ImportedIndividualDetailedFragment } from '../../../../__generated__/graphql';
import { LabelizedField } from '../../../../components/LabelizedField';
import { Missing } from '../../../../components/Missing';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: ${({ theme }) => theme.spacing(6)}px;
  margin-bottom: ${({ theme }) => theme.spacing(6)}px;
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface RegistrationIndividualVulnerabilitiesProps {
  individual: ImportedIndividualDetailedFragment;
}

export function RegistrationIndividualVulnerabilities({
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  individual,
}: RegistrationIndividualVulnerabilitiesProps): React.ReactElement {
  return (
    <Overview>
      <Title>
        <Typography variant='h6'>Vulnerabilities</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={4}>
          <LabelizedField label='Disability'>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Working'>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Serious Illness'>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Martial Status'>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Age first Marriage'>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Enrolled in School'>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='School Attendance'>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='School Type'>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Years in School'>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Minutes to School'>
            <Missing />
          </LabelizedField>
        </Grid>
      </Grid>
    </Overview>
  );
}
