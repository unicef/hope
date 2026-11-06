import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { usePaymentPlan } from '@hooks/usePaymentPlan';
import { Typography } from '@mui/material';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

interface PaymentListParametersProps {
  // Currency and dispersion dates are set on the payment plan; shown here read-only.
  paymentPlanId?: string;
}

export const PaymentListParameters = ({
  paymentPlanId,
}: PaymentListParametersProps): ReactElement => {
  const { t } = useTranslation();
  const { data: paymentPlan } = usePaymentPlan(paymentPlanId);
  const paymentPlanValue = (value: string | null | undefined): string => {
    if (!paymentPlan) return '-';
    return value ?? t('Not set on the Payment Plan');
  };
  return (
    <PaperContainer>
      <Title>
        <Typography variant="h6">{t('Parameters')}</Typography>
      </Title>
      <ResponsiveGridContainer spacing={3}>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('Dispersion Start Date')}
            dataCy="group-dispersion-start-date"
          >
            {paymentPlanValue(paymentPlan?.dispersionStartDate)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('Dispersion End Date')}
            dataCy="group-dispersion-end-date"
          >
            {paymentPlanValue(paymentPlan?.dispersionEndDate)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Currency')} dataCy="group-currency">
            {paymentPlanValue(paymentPlan?.currency)}
          </LabelizedField>
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </PaperContainer>
  );
};
