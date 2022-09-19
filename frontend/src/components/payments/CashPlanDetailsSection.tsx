import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { countPercentage } from '../../utils/utils';
import { CashPlanQuery } from '../../__generated__/graphql';
import { BlackLink } from '../core/BlackLink';
import { LabelizedField } from '../core/LabelizedField';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';

const ChartContainer = styled.div`
  width: 150px;
  height: 150px;
`;

const BorderLeftBox = styled.div`
  padding-left: ${({ theme }) => theme.spacing(6)}px;
  border-left: 1px solid #e0e0e0;
  height: 100%;
`;

interface CashPlanDetailsSectionProps {
  cashPlan: CashPlanQuery['cashPlan'];
}

export const CashPlanDetailsSection = ({
  cashPlan,
}: CashPlanDetailsSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();

  const bankReconciliationSuccessPercentage = countPercentage(
    cashPlan.bankReconciliationSuccess,
    cashPlan.paymentItems.totalCount,
  );

  const bankReconciliationErrorPercentage = countPercentage(
    cashPlan.bankReconciliationError,
    cashPlan.paymentItems.totalCount,
  );

  return (
    <Grid container>
      <Grid item xs={9}>
        <Title>
          <Typography variant='h6'>{t('Cash Plan Details')}</Typography>
        </Title>
        <Grid container>
          {[
            { label: t('PROGRAMME NAME'), value: cashPlan.program.name },
            {
              label: t('PROGRAMME ID'),
              value: (
                <BlackLink
                  to={`/${businessArea}/programs/${cashPlan.program.id}`}
                >
                  {cashPlan.program?.caId}
                </BlackLink>
              ),
            },
            {
              label: t('PAYMENT RECORDS'),
              value: cashPlan.availablePaymentRecordsCount,
            },
            {
              label: t('START DATE'),
              value: <UniversalMoment>{cashPlan.startDate}</UniversalMoment>,
            },
            {
              label: t('END DATE'),
              value: <UniversalMoment>{cashPlan.endDate}</UniversalMoment>,
            },
          ].map((el) => (
            <Grid item xs={4} key={el.label}>
              <Box pt={2} pb={2}>
                <LabelizedField label={el.label}>{el.value}</LabelizedField>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Grid>
      <Grid item xs={3}>
        <BorderLeftBox>
          <Title>
            <Typography variant='h6'>{t('Bank reconciliation')}</Typography>
          </Title>
          <Grid container>
            <Grid item xs={6}>
              <Grid container direction='column'>
                <LabelizedField label={t('SUCCESSFUL')}>
                  <p>{bankReconciliationSuccessPercentage}%</p>
                </LabelizedField>
                <LabelizedField label={t('ERRONEOUS')}>
                  <p>{bankReconciliationErrorPercentage}%</p>
                </LabelizedField>
              </Grid>
            </Grid>
            <Grid item xs={6}>
              <ChartContainer>
                <Doughnut
                  width={200}
                  height={200}
                  options={{
                    maintainAspectRatio: false,
                    cutoutPercentage: 80,
                    legend: {
                      display: false,
                    },
                  }}
                  data={{
                    labels: [t('SUCCESSFUL'), t('ERRONEOUS')],
                    datasets: [
                      {
                        data: [
                          bankReconciliationSuccessPercentage,
                          bankReconciliationErrorPercentage,
                        ],
                        backgroundColor: ['#00509F', '#FFAA1F'],
                        hoverBackgroundColor: ['#00509F', '#FFAA1F'],
                      },
                    ],
                  }}
                />
              </ChartContainer>
            </Grid>
          </Grid>
        </BorderLeftBox>
      </Grid>
    </Grid>
  );
};
