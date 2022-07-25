import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { MiśTheme } from '../../../theme';
import { cashPlanStatusToColor } from '../../../utils/utils';
import { CashPlanNode } from '../../../__generated__/graphql';
import { ContainerWithBorder } from '../ContainerWithBorder';
import { ContentLink } from '../ContentLink';
import { LabelizedField } from '../LabelizedField';
import { OverviewContainer } from '../OverviewContainer';
import { StatusBox } from '../StatusBox';
import { Title } from '../Title';
import { UniversalMoment } from '../UniversalMoment';

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
interface CashPlanProps {
  cashPlan: CashPlanNode;
  businessArea: string;
}

export function CashPlanDetails({
  cashPlan,
  businessArea,
}: CashPlanProps): React.ReactElement {
  const { t } = useTranslation();

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
      <Box display='flex' flexDirection='column'>
        <Title>
          <Typography variant='h6'>{t('Cash Plan Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            <Grid item xs={4}>
              <LabelizedField label={t('Status')}>
                <StatusBox
                  status={cashPlan.status}
                  statusToColor={cashPlanStatusToColor}
                />
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('Plan Start Date')}
                value={<UniversalMoment>{cashPlan?.startDate}</UniversalMoment>}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('Plan End Date')}
                value={<UniversalMoment>{cashPlan?.endDate}</UniversalMoment>}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('cash plan name')}
                value={cashPlan.name}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('delivery type')}
                value={cashPlan.deliveryType}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('assistance through')}
                value={cashPlan.serviceProvider?.fullName}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('dispertion date')}
                value={
                  <UniversalMoment>{cashPlan?.dispersionDate}</UniversalMoment>
                }
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('fc id')}
                value={cashPlan.fundsCommitment}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label={t('dp id')} value={cashPlan.downPayment} />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('Target population(s)')}
                value={renderTargetPopulations()}
              />
            </Grid>
          </Grid>
          <NumberOfHouseHolds>
            <LabelizedField label={t('Total Number of Households')}>
              <NumberOfHouseHoldsValue>
                {cashPlan.totalNumberOfHouseholds}
              </NumberOfHouseHoldsValue>
            </LabelizedField>
          </NumberOfHouseHolds>
        </OverviewContainer>
      </Box>
    </ContainerWithBorder>
  );
}
