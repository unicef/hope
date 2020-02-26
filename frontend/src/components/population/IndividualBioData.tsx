import React from 'react';
import styled from 'styled-components';
import { Paper, Typography, Grid } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import { IndividualNode } from '../../__generated__/graphql';
import moment from 'moment';
import { getAgeFromDob } from '../../utils/utils';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface IndividualBioDataProps {
  individual: IndividualNode;
}
export function IndividualsBioData({
  individual,
}: IndividualBioDataProps): React.ReactElement {
  let age: number | null;
  const { dob } = individual;
  if (dob) {
    age = getAgeFromDob(dob);
  }
  return (
    <Overview>
      <Title>
        <Typography variant='h6'>Bio Data</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={4}>
          <LabelizedField label='Full Name'>
            <div>{individual.fullName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Given Name'>
            <div>{individual.firstName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Middle Name'>
            <div>-</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Family Name'>
            <div>{individual.lastName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Sex'>
            <div>{individual.sex}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Age'>
            <div>{age}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Date of Birth'>
            <div>{dob}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Estimated Date of Birth'>
            <div>
              {individual.estimatedDob ? individual.estimatedDob : 'No'}
            </div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='ID Type'>
            <div>{individual.identificationType}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='ID Number'>
            <div>{individual.identificationNumber}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Household ID'>
            <div>{individual.household.id}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Special Privileges'>
            <div>-</div>
          </LabelizedField>
        </Grid>
      </Grid>
    </Overview>
  );
}
