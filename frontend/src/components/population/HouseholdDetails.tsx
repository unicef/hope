import React from 'react';
import styled from 'styled-components';
import { Typography, Grid, Paper } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
} from '../../__generated__/graphql';
import { choicesToDict, formatCurrencyWithSymbol } from '../../utils/utils';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContentLink } from '../ContentLink';

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
const OverviewPaper = styled(Paper)`
  margin: 20px 20px 0 20px;
  padding: 20px ${({ theme }) => theme.spacing(11)}px;
`;
const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface HouseholdDetailsProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
}
export function HouseholdDetails({
  household,
  choicesData,
}: HouseholdDetailsProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const residenceChoicesDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  return (
    <>
      <Container>
        <Title>
          <Typography variant='h6'>Details</Typography>
        </Title>
        <Overview>
          <Grid container spacing={3}>
            <Grid item xs={3}>
              <LabelizedField label='Household Size'>
                {household.size}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Residence Status'>
                {residenceChoicesDict[household.residenceStatus]}
              </LabelizedField>
            </Grid>
            <Grid item xs={6}>
              <LabelizedField label='Head of Household'>
                <ContentLink
                  href={`/${businessArea}/population/individuals/${household.headOfHousehold.id}`}
                >
                  {household.headOfHousehold.fullName}
                </ContentLink>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='FEMALE CHILD HEADED HOUSEHOLD'>
                {household.fchildHoh ? 'Yes' : 'No'}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='CHILD HEADED HOUSEHOLD'>
                {household.childHoh ? 'Yes' : 'No'}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Country'>
                {household.country}
              </LabelizedField>
            </Grid>

            <Grid item xs={3}>
              <LabelizedField label='Country of Origin'>
                {household.countryOrigin}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Address'>
                {household.address}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Village'>
                {household.village}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Administrative Level 1'>
                {household.admin1?.title}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Administrative Level 2'>
                {household.admin2?.title}
              </LabelizedField>
            </Grid>
            <Grid item xs={6}>
              <LabelizedField label='Geolocation'>
                {household.geopoint
                  ? `${household.geopoint.coordinates[0]}, ${household.geopoint.coordinates[1]}`
                  : '-'}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='UNHCR CASE ID'>
                {household?.unhcrId}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='LENGTH OF TIME SINCE ARRIVAL'>
                {household.flexFields?.months_displaced_h_f}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='NUMBER OF TIMES DISPLACED'>
                {household.flexFields?.number_times_displaced_h_f}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='IS THIS A RETURNEE HOUSEHOLD?'>
                {household.returnee ? 'Yes' : 'No'}
              </LabelizedField>
            </Grid>
          </Grid>
        </Overview>
      </Container>
      <OverviewPaper>
        <Title>
          <Typography variant='h6'>Benefits</Typography>
        </Title>
        <Grid container>
          <Grid item xs={4}>
            <LabelizedField label='Total Cash Received'>
              {formatCurrencyWithSymbol(
                household.totalCashReceived,
                household.currency,
              )}
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='PrOgRAmmE(S) ENROLLED'>
              <div>
                {household.programs.edges.length
                  ? household.programs.edges.map((item) => (
                      <ContentLink
                        key={item.node.id}
                        href={`/${businessArea}/programs/${item.node.id}`}
                      >
                        {item.node.name}
                      </ContentLink>
                    ))
                  : '-'}
              </div>
            </LabelizedField>
          </Grid>
        </Grid>
      </OverviewPaper>
    </>
  );
}
