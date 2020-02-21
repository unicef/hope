import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import { Typography, Grid } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import { HouseholdDetails } from '../../components/population/HouseholdDetails';
import { PageHeader } from '../../components/PageHeader';
import {
  useHouseholdQuery,
  HouseholdNode,
  CashPlanNode,
} from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { HouseholdVulnerabilities } from '../../components/population/HouseholdVulnerabilities';
import { HouseholdActivityTable } from '../HouseholdActivityTable';
import { LabelizedField } from '../../components/LabelizedField';
import { PaymentRecordTable } from '../PaymentRecordTable';
import { HouseholdIndividualsTable } from '../HouseholdIndividualsTable';

const Container = styled.div`
padding 20px;
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

  if (loading) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Household Details',
      to: `/${businessArea}/population/household`,
    },
  ];

  const { household } = data;
  const cashPlan = household.paymentRecords.edges[0].node
    .cashPlan as CashPlanNode;

  return (
    <div>
      <PageHeader
        title={`Household ID: ${id}`}
        breadCrumbs={breadCrumbsItems}
      />
      <HouseholdDetails houseHold={household as HouseholdNode} />
      <Container>
        <HouseholdIndividualsTable household={household as HouseholdNode} />
        <PaymentRecordTable cashPlan={cashPlan} />
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
          <HouseholdActivityTable household={data.household as HouseholdNode} />
        </Content>
      </Container>
    </div>
  );
}
