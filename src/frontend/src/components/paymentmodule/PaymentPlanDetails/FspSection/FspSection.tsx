import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '@generated/graphql';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { VolumeByDeliveryMechanismSection } from './VolumeByDeliveryMechanismSection';
import { ReactElement } from 'react';

interface FspSectionProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const FspSection = ({ paymentPlan }: FspSectionProps): ReactElement => {
  const { t } = useTranslation();

  const { deliveryMechanism, financialServiceProvider } = paymentPlan;

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
