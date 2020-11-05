import React from 'react';
import styled from 'styled-components';
import { Typography, Grid, Paper } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
} from '../../__generated__/graphql';
import { choicesToDict, formatCurrency } from '../../utils/utils';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { MiśTheme } from '../../theme';
import { Missing } from '../Missing';

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
  padding: 20px;
  ${({ theme }) => theme.spacing(11)}px;
`;
const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const ContentLink = styled.a`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 14px;
  line-height: 19px;
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
                <div>{household.size}</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Residence Status'>
                <div>{residenceChoicesDict[household.residenceStatus]}</div>
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
              <LabelizedField label='Country'>
                <div>{household.country || '-'}</div>
              </LabelizedField>
            </Grid>

            <Grid item xs={3}>
              <LabelizedField label='Country of Origin'>
                <div>{household.countryOrigin}</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Address'>
                <div>
                  <div>{household.address}</div>
                </div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Village'>
                <div>
                  <div>{household.village || '-'}</div>
                </div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Administrative Level 1'>
                <div>{household.address || '-'}</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='Administrative Level 2'>
                <div>{household.adminArea?.title || '-'}</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={6}>
              <LabelizedField label='Geolocation'>
                <div>{household.geopoint || '-'}</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='UNHCR CASE ID'>
                <div>
                  <Missing />
                </div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='LENGTH OF TIME SINCE ARRIVAL'>
                <div>
                  <Missing />
                </div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label='NUMBER OF TIMES DISPLACED'>
                <div>
                  <Missing />
                </div>
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
              <div>{formatCurrency(household.totalCashReceived)}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='PrOgRAmmE(S) ENROLLED'>
              <div>
                {household.programs.edges.map((item) => (
                  <ContentLink
                    href={`/${businessArea}/programs/${item.node.id}`}
                  >
                    {item.node.name}
                  </ContentLink>
                ))}
              </div>
            </LabelizedField>
          </Grid>
        </Grid>
      </OverviewPaper>
    </>
  );
}
