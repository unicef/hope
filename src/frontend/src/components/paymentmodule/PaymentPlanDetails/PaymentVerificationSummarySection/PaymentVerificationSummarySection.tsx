import { Box, Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentVerificationPlan } from '@restgenerated/models/PaymentVerificationPlan';
import { paymentVerificationStatusToColor } from '@utils/utils';
import { ReactElement } from 'react';

interface PaymentVerificationSummarySectionProps {
  paymentPlan: PaymentPlanDetail;
}

function PaymentVerificationSummarySection({
  paymentPlan,
}: PaymentVerificationSummarySectionProps): ReactElement {
  const { t } = useTranslation();
  const { paymentVerificationSummary } = paymentPlan;
  const verificationPlans = paymentPlan.paymentVerificationPlans ?? [];

  const sumBy = (
    selector: (plan: PaymentVerificationPlan) => number | null | undefined,
  ): number =>
    verificationPlans.reduce((acc, plan) => acc + (selector(plan) ?? 0), 0);

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Typography variant="h6">
              {t('Payment Verification Summary')}
            </Typography>
          </Title>
        </Box>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Status')}>
              <StatusBox
                dataCy="payment-verification-summary-status"
                status={paymentVerificationSummary?.status}
                statusToColor={paymentVerificationStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Number of Verification Plans')}
              value={paymentVerificationSummary?.numberOfVerificationPlans}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Activation Date')}>
              <UniversalMoment>
                {paymentVerificationSummary?.activationDate}
              </UniversalMoment>
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Completion Date')}>
              <UniversalMoment>
                {paymentVerificationSummary?.completionDate}
              </UniversalMoment>
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Sample Size')}
              value={sumBy((plan) => plan.sampleSize)}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Responded')}
              value={sumBy((plan) => plan.respondedCount)}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Received')}
              value={sumBy((plan) => plan.receivedCount)}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Not Received')}
              value={sumBy((plan) => plan.notReceivedCount)}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Received with Issues')}
              value={sumBy((plan) => plan.receivedWithProblemsCount)}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
    </Box>
  );
}

export default withErrorBoundary(
  PaymentVerificationSummarySection,
  'PaymentVerificationSummarySection',
);
