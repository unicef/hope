import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { usePaymentPlanGroup } from '@hooks/usePaymentPlanGroup';
import { Grid, Typography } from '@mui/material';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaperContainer } from '../../../targeting/PaperContainer';

interface PaymentPlanParametersProps {
  // Currency and dispersion dates are set on the group; shown here read-only.
  paymentPlanGroupId?: string;
}

export const PaymentPlanParameters = ({
  paymentPlanGroupId,
}: PaymentPlanParametersProps): ReactElement => {
  const { t } = useTranslation();
  const { data: paymentPlanGroup } = usePaymentPlanGroup(paymentPlanGroupId);
  const groupValue = (value: string | null | undefined): string => {
    if (!paymentPlanGroup) return '-';
    return value ?? t('Not set on the Payment Plan');
  };
  return (
    <PaperContainer>
      <Title>
        <Typography variant="h6">{t('Parameters')}</Typography>
      </Title>
      <Grid spacing={3} container>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={t('Dispersion Start Date')}
            dataCy="group-dispersion-start-date"
          >
            {groupValue(paymentPlanGroup?.dispersionStartDate)}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={t('Dispersion End Date')}
            dataCy="group-dispersion-end-date"
          >
            {groupValue(paymentPlanGroup?.dispersionEndDate)}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Currency')} dataCy="group-currency">
            {groupValue(paymentPlanGroup?.currency)}
          </LabelizedField>
        </Grid>
      </Grid>
    </PaperContainer>
  );
};
