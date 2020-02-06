import React from 'react';
import styled from 'styled-components';
import moment from 'moment';
import { Grid, Typography } from '@material-ui/core';
import { CashPlanNode } from '../__generated__/graphql';
import { LabelizedField } from './LabelizedField';
import { StatusBox } from './StatusBox';
import { MiśTheme } from '../theme';
import { cashPlanStatusToColor } from '../utils/utils';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;
const OverviewContainer = styled.div`
  display: flex;
  align-items: center;
  flex-direction: row;
`;

const StatusContainer = styled.div`
  width: 120px;
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
    cashPlan: CashPlanNode
}

export function CashPlanDetails({
    cashPlan
}: CashPlanProps): React.ReactElement {
    return (
        <Container>
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
                label='START DATE'
                value={moment(cashPlan.startDate).format('DD MMM YYYY')}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label='END DATE'
                value={moment(cashPlan.endDate).format('DD MMM YYYY')}
              />
            </Grid>
            <Grid item xs={4}>
                <LabelizedField label='dispertion date' value={cashPlan.dispersionDate} />
            </Grid>
            <Grid item xs={4}>
                <LabelizedField label='target population' value={cashPlan.targetPopulation.name} />
            </Grid>
          </Grid>
          <NumberOfHouseHolds>
            <LabelizedField label='Total Number of Households'>
              <NumberOfHouseHoldsValue>
                123
              </NumberOfHouseHoldsValue>
            </LabelizedField>
          </NumberOfHouseHolds>
        </OverviewContainer>
      </Container>
    )
}