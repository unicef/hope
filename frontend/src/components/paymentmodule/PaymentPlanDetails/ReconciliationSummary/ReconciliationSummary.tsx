import React from 'react';
import { Grid, Typography } from '@material-ui/core';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { LabelizedField } from '../../../core/LabelizedField';
import { FieldBorder } from '../../../core/FieldBorder';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
  margin: 0 auto;
`;

const ReconciliationWrapUp = styled.div`
  padding-bottom: 8px;
`;

interface ReconciliationSummaryProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const ReconciliationSummary = ({
  paymentPlan,
}: ReconciliationSummaryProps): React.ReactElement => {
  const { t } = useTranslation();

  const {
    reconciliationSummary: {
      deliveredFully,
      deliveredPartially,
      unsuccessful,
      notDelivered,
      numberOfPayments,
      pending,
      reconciled,
    },
  } = paymentPlan;

  const datasets = [
    {
      label: t('Delivered fully'),
      value: deliveredFully,
      color: '#10CB16',
    },
    {
      label: t('Delivered partially'),
      value: deliveredPartially,
      color: '#FC942A',
    },
    {
      label: t('Not delivered'),
      value: notDelivered,
      color: '#EF4343',
    },
    {
      label: t('Unsuccessful'),
      value: unsuccessful,
      color: '#EF4343',
    },
    {
      label: t('Pending'),
      value: pending,
      color: '#4E606A',
    },
  ];

  const reconciledInPercent = ((reconciled / numberOfPayments) * 100).toFixed(
    0,
  );
  return (
    <>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{t('Reconciliation Summary')}</Typography>
        </Title>
        <ContentWrapper>
          <Grid container>
            <Grid item xs={12}>
              <Grid item xs={12}>
                <Grid container spacing={0} justifyContent='flex-start'>
                  {datasets.map(({ color, label, value }) => (
                    <Grid item xs={2} key={label}>
                      <FieldBorder color={color}>
                        <LabelizedField label={label} value={value} />
                      </FieldBorder>
                    </Grid>
                  ))}
                  <Grid item xs={2}>
                    <ChartContainer data-cy='chart-container'>
                      <Pie
                        width={100}
                        height={100}
                        options={{
                          legend: {
                            display: false,
                          },
                        }}
                        data={{
                          labels: datasets.map(({ label }) => label),
                          datasets: [
                            {
                              data: datasets.map(({ value }) => value),
                              backgroundColor: datasets.map(
                                ({ color }) => color,
                              ),
                            },
                          ],
                        }}
                      />
                    </ChartContainer>
                  </Grid>
                </Grid>
              </Grid>
              <ReconciliationWrapUp>
                <Grid item xs={12}>
                  <Grid container spacing={0} justifyContent='flex-start'>
                    <Grid item xs={2}>
                      <FieldBorder color='#4E606A'>
                        <LabelizedField
                          label={t('Number of payments')}
                          value={numberOfPayments}
                        />
                      </FieldBorder>
                    </Grid>
                    <Grid item xs={2}>
                      <FieldBorder color='#4E606A'>
                        <LabelizedField
                          label={t('Reconciled')}
                          value={`${reconciled} (${reconciledInPercent}%)`}
                        />
                      </FieldBorder>
                    </Grid>
                  </Grid>
                </Grid>
              </ReconciliationWrapUp>
            </Grid>
          </Grid>
        </ContentWrapper>
      </PaperContainer>
    </>
  );
};
