import React from 'react';
import styled from 'styled-components';
import { Typography, Grid } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import { HouseholdNode } from '../../__generated__/graphql';
import { formatCurrency } from '../../utils/utils';

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
  houseHold: HouseholdNode;
}
export function HouseholdDetails({
  houseHold,
}: HouseholdDetailsProps): React.ReactElement {
  const { paymentRecords } = houseHold;
  return (
    <Container>
      <Title>
        <Typography variant='h6'>Details</Typography>
      </Title>
      <Overview>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='Household Size'>
              <div>{houseHold.familySize ? houseHold.familySize : 0}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Location'>
              <div>{houseHold.location.title}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Residence Status'>
              <div>{houseHold.residenceStatus}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Family Nationality'>
              <div>{houseHold.nationality}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Household Size'>
              <div>
                {paymentRecords.edges.length
                  ? paymentRecords.edges[0].node.headOfHousehold
                  : ''}
              </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Total Cash Received'>
              <div>
                {paymentRecords.edges.length
                  ? formatCurrency(
                      paymentRecords.edges[0].node.cashPlan
                        .totalDeliveredQuantity,
                    )
                  : ''}
              </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Programme(s)'>
              <div>
                {paymentRecords.edges.length
                  ? paymentRecords.edges[0].node.cashPlan.program.name
                  : ''}
              </div>
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </Container>
  );
}
