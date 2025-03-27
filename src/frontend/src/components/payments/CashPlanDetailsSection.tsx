import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { countPercentage } from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

const ChartContainer = styled.div`
  width: 100%;
  height: 100%;
`;

const BorderLeftBox = styled.div`
  padding-left: ${({ theme }) => theme.spacing(6)};
  border-left: 1px solid #e0e0e0;
  height: 100%;
`;

interface CashPlanDetailsSectionProps {
  planNode: PaymentPlanDetail;
}

export function CashPlanDetailsSection({
  planNode,
}: CashPlanDetailsSectionProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const bankReconciliationSuccessPercentage = countPercentage(
    planNode.bank_reconciliation_success,
    planNode.payment_items_total_count,
  );

  const bankReconciliationErrorPercentage = countPercentage(
    planNode.bank_reconciliation_error,
    planNode.payment_items_total_count,
  );

  return (
    <Grid container>
      <Grid size={{ xs: 7 }}>
        <Title data-cy="div-payment-plan-details">
          <Typography variant="h6">{t('Payment Plan Details')}</Typography>
        </Title>
        <Box pr={2}>
          <Grid data-cy="grid-payment-plan-details" container spacing={3}>
            {[
              {
                label: t('PROGRAMME NAME'),
                value: (
                  <BlackLink to={`/${baseUrl}/details/${planNode.program.id}`}>
                    {planNode.program.name}
                  </BlackLink>
                ),
              },
              {
                label: t('PAYMENT RECORDS'),
                value: planNode.available_payment_records_count,
              },
              {
                label: t('START DATE'),
                value: <UniversalMoment>{planNode.start_date}</UniversalMoment>,
              },
              {
                label: t('END DATE'),
                value: <UniversalMoment>{planNode.end_date}</UniversalMoment>,
              },
            ].map((el) => (
              <Grid size={{ xs: 3 }} key={el.label}>
                <LabelizedField label={el.label}>{el.value}</LabelizedField>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Grid>
      <Grid data-cy="grid-bank-reconciliation" size={{ xs: 5 }}>
        <BorderLeftBox>
          <Title>
            <Typography variant="h6" data-cy="table-label">
              {t('Bank reconciliation')}
            </Typography>
          </Title>
          <Grid container>
            <Grid size={{ xs: 3 }}>
              <Grid container direction="column">
                <LabelizedField label={t('SUCCESSFUL')}>
                  <p>{bankReconciliationSuccessPercentage}%</p>
                </LabelizedField>
                <LabelizedField label={t('ERRONEOUS')}>
                  <p>{bankReconciliationErrorPercentage}%</p>
                </LabelizedField>
              </Grid>
            </Grid>
            <Grid size={{ xs: 9 }}>
              <ChartContainer>
                <Doughnut
                  options={
                    {
                      maintainAspectRatio: false,
                      cutout: '80%',
                      plugins: {
                        legend: {
                          display: false,
                        },
                      },
                    } as any
                  }
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
}
