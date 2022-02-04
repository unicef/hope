import { Box, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { AllChartsQuery } from '../../../__generated__/graphql';
import { PaymentVerificationChart } from '../charts/PaymentVerificationChart';
import { DashboardPaper } from '../DashboardPaper';

interface PaymentVerificationSectionProps {
  data: AllChartsQuery['chartPaymentVerification'];
}
export const PaymentVerificationSection = ({
  data,
}: PaymentVerificationSectionProps): React.ReactElement => {
  const { t } = useTranslation();

  if (!data) return null;
  return (
    <DashboardPaper title={t('Payment Verification')}>
      <Box mt={3}>
        <Typography variant='subtitle2'>
          {data.households}{' '}
          {data.households === 1 ? t('Household') : t('Households contacted')}
        </Typography>
        <Typography variant='caption'>
          {(data.averageSampleSize * 100).toFixed(0)}% {t('average sampling')}
        </Typography>
      </Box>
      <PaymentVerificationChart data={data} />
    </DashboardPaper>
  );
};
