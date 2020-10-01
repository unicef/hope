import React from 'react';
import styled from 'styled-components';
import { Typography, Grid } from '@material-ui/core';
import { LabelizedField } from '../../../../components/LabelizedField';
import {
  HouseholdChoiceDataQuery,
  ImportedHouseholdDetailedFragment,
} from '../../../../__generated__/graphql';
import { MiśTheme } from '../../../../theme';
import { Missing } from '../../../../components/Missing';
import { choicesToDict, formatCurrency } from '../../../../utils/utils';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';

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
const ContentLink = styled.a`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 14px;
  line-height: 19px;
`;
interface HouseholdDetailsProps {
  household: ImportedHouseholdDetailedFragment;
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
    <Container>
      <Title>
        <Typography variant='h6'>Details</Typography>
      </Title>
      <Overview>
        <Grid container spacing={6}>
          <Grid item xs={3}>
            <LabelizedField label='Household Size'>
              <div>{household.size}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Location'>
              <div>{household.country}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Residence Status'>
              <div>{residenceChoicesDict[household.residenceStatus]}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Country of Origin'>
              <div>{household.countryOrigin}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Head of Household'>
              <ContentLink
                href={`/${businessArea}/registration-data-import/individual/${household.headOfHousehold.id}`}
              >
                {household.headOfHousehold.fullName}
              </ContentLink>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Total Cash Received'>
              <div>
                <Missing />
                {/* <div>{formatCurrency(household.totalCashReceived)}</div> */}
              </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='Programme (Enrolled)'>
              <div>
                <Missing />
              </div>
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </Container>
  );
}
