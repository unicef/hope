import React from 'react';
import styled from 'styled-components';
import { Typography, Grid } from '@material-ui/core';
import { LabelizedField } from '../../../../components/LabelizedField';
import { ImportedHouseholdDetailedFragment } from '../../../../__generated__/graphql';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  align-items: center;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;

  && > div {
    margin: 5px;
  }
`;

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
    <Container>
      <Title>
        <Typography variant='h6'>Details</Typography>
      </Title>
      <Overview>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='Household Size'>
              <div>{household.familySize}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Location'>
              <div>{household.location}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Residence Status'>
              <div>{household.residenceStatus}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Family Nationality'>
              <div>{household.nationality}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Head of Household'>
              <div>{household.headOfHousehold.fullName}</div>
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </Container>
  );
}
