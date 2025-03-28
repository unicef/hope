import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { VolumeByDeliveryMechanismSection } from './VolumeByDeliveryMechanismSection';

interface FspSectionProps {
  paymentPlan: PaymentPlanDetail;
}

export const FspSection = ({ paymentPlan }: FspSectionProps): ReactElement => {
  const { t } = useTranslation();

  const { delivery_mechanism, fsp } = paymentPlan;

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
              key={`${delivery_mechanism.name}-${fsp.name}`}
              size={{ xs: 3 }}
            >
              <LabelizedField
                label={delivery_mechanism.name || '-'}
                value={fsp.name || '-'}
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
