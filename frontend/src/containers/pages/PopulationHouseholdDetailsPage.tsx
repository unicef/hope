import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import { Grid, Typography } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import { HouseholdDetails } from '../../components/population/HouseholdDetails';
import { PageHeader } from '../../components/PageHeader';
import {
  CashPlanNode,
  HouseholdNode,
  useHouseholdChoiceDataQuery,
  useHouseholdQuery,
} from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { HouseholdVulnerabilities } from '../../components/population/HouseholdVulnerabilities';
import { LabelizedField } from '../../components/LabelizedField';
import { PaymentRecordTable } from '../tables/PaymentRecordTable';
import { HouseholdIndividualsTable } from '../tables/HouseholdIndividualsTable';
import { UniversalActivityLogTable } from '../tables/UniversalActivityLogTable';
import { decodeIdString } from '../../utils/utils';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: 20px;
  &:first-child {
    margin-top: 0px;
  }
`;
const Content = styled.div`
  margin-top: 20px;
`;

export function PopulationHouseholdDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const { data, loading } = useHouseholdQuery({
    variables: { id },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery({
    variables: { businessArea },
  });
  if (loading || choicesLoading) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Households',
      to: `/${businessArea}/population/household`,
    },
  ];

  const { household } = data;
  const cashPlan = household.paymentRecords.edges[0].node
    .cashPlan as CashPlanNode;

  return (
    <div>
      <PageHeader
        title={`Household ID: ${decodeIdString(id)}`}
        breadCrumbs={breadCrumbsItems}
      />
      <HouseholdDetails houseHold={household as HouseholdNode} />
      <Container>
        <HouseholdIndividualsTable
          choicesData={choicesData}
          household={household as HouseholdNode}
        />
        <PaymentRecordTable openInNewTab cashPlan={cashPlan} />
        <HouseholdVulnerabilities />
        <Overview>
          <Title>
            <Typography variant='h6'>Registration Details</Typography>
          </Title>
          <Grid container spacing={6}>
            <Grid item xs={4}>
              <LabelizedField label='Source'>
                <div>-</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='Intake group name'>
                <div>-</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='Registered Date'>
                <div>-</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='Number of Rooms'>
                <div>-</div>
              </LabelizedField>
            </Grid>
          </Grid>
          <hr />
          <Typography variant='h6'>Data Collection</Typography>
          <Grid container spacing={6}>
            <Grid item xs={4}>
              <LabelizedField label='Start time'>
                <div>-</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='End time'>
                <div>-</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='Device ID'>
                <div>-</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='User name'>
                <div>-</div>
              </LabelizedField>
            </Grid>
          </Grid>
        </Overview>
        <Content>
          <UniversalActivityLogTable objectId={data.household.id} />
        </Content>
      </Container>
    </div>
  );
}
