import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import withErrorBoundary from '@components/core/withErrorBoundary';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import type { PaymentVerificationPlan } from '@restgenerated/models/PaymentVerificationPlan';
import { paymentVerificationStatusToColor } from '@utils/utils';
import type { ReactElement } from 'react';
import {
  responsiveValue,
  ResponsiveGrid,
  ResponsiveGridContainer,
} from 'src/responsive';

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
    <Box
      sx={{
        m: responsiveValue(2, 5),
      }}
    >
      <ContainerColumnWithBorder>
        <Box
          sx={{
            mt: 4,
          }}
        >
          <Title>
            <Typography variant="h6">
              {t('Payment Verification Summary')}
            </Typography>
          </Title>
        </Box>
        <ResponsiveGridContainer spacing={3}>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Status')}>
              <StatusBox
                dataCy="payment-verification-summary-status"
                status={paymentVerificationSummary?.status}
                statusToColor={paymentVerificationStatusToColor}
              />
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('Number of Verification Plans')}
              value={paymentVerificationSummary?.numberOfVerificationPlans}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Activation Date')}>
              <UniversalMoment>
                {paymentVerificationSummary?.activationDate}
              </UniversalMoment>
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Completion Date')}>
              <UniversalMoment>
                {paymentVerificationSummary?.completionDate}
              </UniversalMoment>
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('Sample Size')}
              value={sumBy((plan) => plan.sampleSize)}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('Responded')}
              value={sumBy((plan) => plan.respondedCount)}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('Received')}
              value={sumBy((plan) => plan.receivedCount)}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('Not Received')}
              value={sumBy((plan) => plan.notReceivedCount)}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('Received with Issues')}
              value={sumBy((plan) => plan.receivedWithProblemsCount)}
            />
          </ResponsiveGrid>
        </ResponsiveGridContainer>
      </ContainerColumnWithBorder>
    </Box>
  );
}

export default withErrorBoundary(
  PaymentVerificationSummarySection,
  'PaymentVerificationSummarySection',
);
