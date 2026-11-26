import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { Box, Grid, Typography } from '@mui/material';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { VolumeByDeliveryMechanismSection } from './VolumeByDeliveryMechanismSection';

interface FspSectionProps {
  paymentList: PaymentListDetail;
}

export const FspSection = ({ paymentList }: FspSectionProps): ReactElement => {
  const { t } = useTranslation();

  return (
    <Box
      sx={{
        m: 5,
      }}
    >
      <ContainerColumnWithBorder>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: 4,
          }}
        >
          <Typography variant="h6">{t('FSPs')}</Typography>
        </Box>
        <Grid container spacing={3}>
          <>
            <Grid
              key={`${paymentList.deliveryMechanism?.name}-${paymentList?.financialServiceProvider?.name}`}
              size={{ xs: 3 }}
            >
              <LabelizedField
                label={paymentList.deliveryMechanism?.name || '-'}
                value={paymentList.financialServiceProvider?.name || '-'}
              />
            </Grid>
          </>
        </Grid>
        <DividerLine />
        <VolumeByDeliveryMechanismSection paymentList={paymentList} />
      </ContainerColumnWithBorder>
    </Box>
  );
};
