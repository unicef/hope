import React from 'react';
import styled from 'styled-components';
import { Typography, Grid } from '@material-ui/core';
import { LabelizedField } from '../../../../components/LabelizedField';
import { ImportedHouseholdDetailedFragment } from '../../../../__generated__/graphql';
import { ContainerWithBorder } from '../../../../components/ContainerWithBorder';

const Overview = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
`;
const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface HouseholdDetailsProps {
  household: ImportedHouseholdDetailedFragment;
}
export function HouseholdDetails({
  household,
}: HouseholdDetailsProps): React.ReactElement {
  return (
    <ContainerWithBorder>
      <Title>
        <Typography variant='h6'>Details</Typography>
      </Title>
      <Overview>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='Household Size'>
              <div>{household.size}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Country'>
              <div>{household.country}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Residence Status'>
              <div>{household.residenceStatus}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Country of Origin'>
              <div>{household.countryOrigin}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Head of Household'>
              <div>{household.headOfHousehold.fullName}</div>
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </ContainerWithBorder>
  );
}
