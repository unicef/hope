import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { VolumeByDeliveryMechanismSection } from './VolumeByDeliveryMechanismSection';

interface FspSectionProps {
  baseUrl: string;
  paymentPlan: PaymentPlanDetail;
}

export const FspSection = ({ paymentPlan }: FspSectionProps): ReactElement => {
  const { t } = useTranslation();

  const { delivery_mechanisms, is_follow_up, financial_service_provider } =
    paymentPlan;
  const showFspDisplay = delivery_mechanisms?.length;
  const shouldDisableSetUpFsp = (): boolean => {
    if (paymentPlan.is_follow_up) {
      return false;
    }
    if (!paymentPlan.total_entitled_quantity_usd) {
      return true;
    }
    if (!isActiveProgram) {
      return true;
    }
    return false;
  };

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
              key={`${deliveryMechanism?.name}-${financialServiceProvider?.name}`}
              size={{ xs: 3 }}
            >
              <LabelizedField
                label={deliveryMechanism?.name || '-'}
                value={financialServiceProvider?.name || '-'}
              />
            </Grid>
          </>
        </Grid>
        <DividerLine />
        <VolumeByDeliveryMechanismSection paymentPlan={paymentPlan} />
      </ContainerColumnWithBorder>
    </Box>
  );
};
