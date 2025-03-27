import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { VolumeByDeliveryMechanismSection } from './VolumeByDeliveryMechanismSection';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface FspSectionProps {
  baseUrl: string;
  paymentPlan: PaymentPlanDetail;
}

export function FspSection({ paymentPlan }: FspSectionProps): ReactElement {
  const { t } = useTranslation();

  const { delivery_mechanism, financial_service_provider } = paymentPlan;

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mt={4}
        >
          <Typography variant="h6">{t('FSPs')}</Typography>
        </Box>
        <Grid container spacing={3}>
          <>
            <Grid
              key={`${delivery_mechanism?.name}-${financial_service_provider?.name}`}
              size={{ xs: 3 }}
            >
              <LabelizedField
                label={delivery_mechanism?.name || '-'}
                value={financial_service_provider?.name || '-'}
              />
            </Grid>
          </>
        </Grid>
        <DividerLine />
        <VolumeByDeliveryMechanismSection paymentPlan={paymentPlan} />
      </ContainerColumnWithBorder>
    </Box>
  );
}
