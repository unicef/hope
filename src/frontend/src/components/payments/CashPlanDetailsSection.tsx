import { Box, Typography, Grid } from '@mui/material';
import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { countPercentage, formatFigure } from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { ReactElement } from 'react';
import type { PaymentVerificationPlanDetails } from '@restgenerated/models/PaymentVerificationPlanDetails';
import { ResponsiveGrid, responsiveValue } from 'src/responsive';

const ChartContainer = styled.div`
  width: 100%;
  height: 100%;
`;

interface CashPlanDetailsSectionProps {
  planNode: PaymentVerificationPlanDetails;
}

export function CashPlanDetailsSection({
  planNode,
}: CashPlanDetailsSectionProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const bankReconciliationSuccessPercentage = countPercentage(
    planNode.bankReconciliationSuccess,
    planNode.eligiblePaymentsCount,
  );

  const bankReconciliationErrorPercentage = countPercentage(
    planNode.bankReconciliationError,
    planNode.eligiblePaymentsCount,
  );

  return (
    <Grid container rowSpacing={responsiveValue(4, 0)}>
      <Grid size={responsiveValue(12, 7)}>
        <Title data-cy="div-payment-plan-details">
          <Typography variant="h6">{t('Payment Plan Details')}</Typography>
        </Title>
        <Box
          sx={{
            pr: responsiveValue(0, 2),
          }}
        >
          <Grid data-cy="grid-payment-plan-details" container spacing={3}>
            {[
              {
                label: t('PROGRAMME NAME'),
                value: (
                  <BlackLink to={`/${baseUrl}/details/${planNode.programId}`}>
                    {planNode.programName}
                  </BlackLink>
                ),
              },
              {
                label: t('PAYMENT RECORDS'),
                value: formatFigure(planNode.availablePaymentRecordsCount),
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
              <ResponsiveGrid size="quarter" mobileSize="half" key={el.label}>
                <LabelizedField label={el.label}>{el.value}</LabelizedField>
              </ResponsiveGrid>
            ))}
          </Grid>
        </Box>
      </Grid>
      <Grid data-cy="grid-bank-reconciliation" size={responsiveValue(12, 5)}>
        <Box
          sx={{
            pl: responsiveValue(0, 6),
            pt: responsiveValue(4, 0),
            borderLeft: responsiveValue('none', '1px solid #e0e0e0'),
            borderTop: responsiveValue('1px solid #e0e0e0', 'none'),
            height: '100%',
          }}
        >
          <Title>
            <Typography variant="h6" data-cy="table-label">
              {t('Reconciliation Summary')}
            </Typography>
          </Title>
          <Grid container>
            <Grid size={{ xs: 3 }}>
              <Grid container sx={{ flexDirection: 'column' }}>
                <LabelizedField label={t('SUCCESSFUL')}>
                  <p>{formatFigure(bankReconciliationSuccessPercentage)}%</p>
                </LabelizedField>
                <LabelizedField label={t('ERRONEOUS')}>
                  <p>{formatFigure(bankReconciliationErrorPercentage)}%</p>
                </LabelizedField>
              </Grid>
            </Grid>
            <Grid size={{ xs: 9 }}>
              <ChartContainer>
                <Doughnut
                  options={{
                    maintainAspectRatio: false,
                    cutout: '80%',
                    plugins: {
                      legend: {
                        display: false,
                      },
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
        </Box>
      </Grid>
    </Grid>
  );
}
