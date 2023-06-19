import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { countPercentage } from '../../utils/utils';
import { CashPlanQuery, PaymentPlanQuery } from '../../__generated__/graphql';
import { BlackLink } from '../core/BlackLink';
import { LabelizedField } from '../core/LabelizedField';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';
import { useBaseUrl } from '../../hooks/useBaseUrl';

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
  planNode: CashPlanQuery['cashPlan'] | PaymentPlanQuery['paymentPlan'];
}

export const CashPlanDetailsSection = ({
  planNode,
}: CashPlanDetailsSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const bankReconciliationSuccessPercentage = countPercentage(
    planNode.bankReconciliationSuccess,
    planNode.paymentItems.totalCount,
  );

  const bankReconciliationErrorPercentage = countPercentage(
    planNode.bankReconciliationError,
    planNode.paymentItems.totalCount,
  );

  return (
    <Grid container>
      <Grid item xs={9}>
        <Title data-cy='div-payment-plan-details'>
          <Typography variant='h6'>{t('Payment Plan Details')}</Typography>
        </Title>
        <Grid data-cy='grid-payment-plan-details' container>
          {[
            { label: t('PROGRAMME NAME'), value: planNode.program.name },
            {
              label: t('PROGRAMME ID'),
              value: (
                <BlackLink to={`/${baseUrl}/programs/${planNode.program.id}`}>
                  {planNode.program?.caId}
                </BlackLink>
              ),
            },
            {
              label: t('PAYMENT RECORDS'),
              value: planNode.availablePaymentRecordsCount,
            },
            {
              label: t('START DATE'),
              value: <UniversalMoment>{planNode.startDate}</UniversalMoment>,
            },
            {
              label: t('END DATE'),
              value: <UniversalMoment>{planNode.endDate}</UniversalMoment>,
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
      <Grid data-cy='grid-bank-reconciliation' item xs={3}>
        <BorderLeftBox>
          <Title>
            <Typography variant='h6' data-cy='table-label'>
              {t('Bank reconciliation')}
            </Typography>
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
