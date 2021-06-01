import React from 'react';
import styled from 'styled-components';
import { Grid, Typography } from '@material-ui/core';
import { CashPlanNode } from '../__generated__/graphql';
import { MiśTheme } from '../theme';
import { cashPlanStatusToColor } from '../utils/utils';
import { useBusinessArea } from '../hooks/useBusinessArea';
import { LabelizedField } from './LabelizedField';
import { StatusBox } from './StatusBox';
import { UniversalMoment } from './UniversalMoment';
import { ContainerWithBorder } from './ContainerWithBorder';
import { OverviewContainer } from './OverviewContainer';
import { ContentLink } from './ContentLink';

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
  const businessArea = useBusinessArea();

  const filteredTps = (): Array<{
    id: string;
    name: string;
  }> => {
    const mappedTPs = cashPlan.paymentRecords?.edges.map((edge) => ({
      id: edge.node.targetPopulation?.id,
      name: edge.node.targetPopulation?.name,
    }));

    const uniques = [];
    for (const obj of mappedTPs) {
      if (obj && !uniques.find((el) => el?.id === obj?.id)) {
        uniques.push(obj);
      }
    }
    return uniques;
  };

  const renderTargetPopulations = ():
    | React.ReactElement
    | Array<React.ReactElement> => {
    return filteredTps().length ? (
      filteredTps().map((el) => (
        <span key={el.id}>
          <ContentLink href={`/${businessArea}/target-population/${el.id}`}>
            {el.name}
          </ContentLink>{' '}
        </span>
      ))
    ) : (
      <span>-</span>
    );
  };
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
              value={<UniversalMoment>{cashPlan?.startDate}</UniversalMoment>}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='plan end date'
              value={<UniversalMoment>{cashPlan?.endDate}</UniversalMoment>}
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
              value={cashPlan.serviceProvider?.fullName}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='dispertion date'
              value={
                <UniversalMoment>{cashPlan?.dispersionDate}</UniversalMoment>
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
            <LabelizedField
              label='Target population(s)'
              value={renderTargetPopulations()}
            />
          </Grid>
        </Grid>
        <NumberOfHouseHolds>
          <LabelizedField label='Total Number of Households'>
            <NumberOfHouseHoldsValue>{cashPlan.totalNumberOfHouseholds}</NumberOfHouseHoldsValue>
          </LabelizedField>
        </NumberOfHouseHolds>
      </OverviewContainer>
    </ContainerWithBorder>
  );
}
