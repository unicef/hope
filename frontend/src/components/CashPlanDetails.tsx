import React from 'react';
import styled from 'styled-components';
import { Grid, Typography } from '@material-ui/core';
import { CashPlanNode } from '../__generated__/graphql';
import { MiśTheme } from '../theme';
import { cashPlanStatusToColor } from '../utils/utils';
import { LabelizedField } from './LabelizedField';
import { StatusBox } from './StatusBox';
import { Missing } from './Missing';
import { UniversalMoment } from './UniversalMoment';
import { ContainerWithBorder } from './ContainerWithBorder';
import { OverviewContainer } from './OverviewContainer';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

const NumberOfHouseHolds = styled.div`
  padding: ${({ theme }) => theme.spacing(8)}px;
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
`;
const NumberOfHouseHoldsValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface CashPlanProps {
  cashPlan: CashPlanNode;
}

export function CashPlanDetails({
  cashPlan,
}: CashPlanProps): React.ReactElement {
  return (
    <ContainerWithBorder>
      <Title>
        <Typography variant='h6'>Cash Plan Details</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='status'>
              <StatusContainer>
                <StatusBox
                  status={cashPlan.status}
                  statusToColor={cashPlanStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='plan start date'
              value={<UniversalMoment>{cashPlan.startDate}</UniversalMoment>}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='plan end date'
              value={<UniversalMoment>{cashPlan.endDate}</UniversalMoment>}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='cash plan name' value={cashPlan.name} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='delivery type'
              value={cashPlan.deliveryType}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='assistance through'
              value={cashPlan.assistanceThrough}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='dispertion date'
              value={
                <UniversalMoment>{cashPlan.dispersionDate}</UniversalMoment>
              }
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='fc id' value={cashPlan.fundsCommitment} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='dp id' value={cashPlan.downPayment} />
          </Grid>
          <Grid item xs={4}>
            <Missing />
          </Grid>
        </Grid>
        <NumberOfHouseHolds>
          <LabelizedField label='Total Number of Households'>
            <NumberOfHouseHoldsValue>123</NumberOfHouseHoldsValue>
          </LabelizedField>
        </NumberOfHouseHolds>
      </OverviewContainer>
    </ContainerWithBorder>
  );
}
