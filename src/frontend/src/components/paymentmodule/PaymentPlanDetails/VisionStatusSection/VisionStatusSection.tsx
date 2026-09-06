import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { Alert, Box, Grid, Typography } from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface VisionStatusSectionProps {
  paymentPlan: PaymentPlanDetail;
}

const errorStatuses = new Set([
  'SEND_FAILED',
  'CALLBACK_FAILED',
  'FC_MISSING',
  'FC_NOT_FOUND',
]);

export function VisionStatusSection({
  paymentPlan,
}: VisionStatusSectionProps): ReactElement | null {
  const { t } = useTranslation();
  if (!paymentPlan.visionManaged) return null;

  const vision = paymentPlan.vision;
  const status = vision.status;
  const severity = errorStatuses.has(status)
    ? 'error'
    : status === 'FC_ASSOCIATED' || status === 'RELEASED'
      ? 'success'
      : 'info';

  return (
    <Box sx={{ m: 5 }}>
      <ContainerColumnWithBorder>
        <Box sx={{ mt: 4 }}>
          <Title>
            <Typography variant="h6">{t('Vision Integration')}</Typography>
          </Title>
        </Box>
        <Alert severity={severity} sx={{ mb: 3 }}>
          {t(status.replaceAll('_', ' '))}
          {vision.errorCode
            ? `: ${t(vision.errorCode.replaceAll('_', ' '))}`
            : ''}
        </Alert>
        <Grid container spacing={3}>
          <Grid size={{ xs: 6 }}>
            <LabelizedField
              label={t('Vision Payment Plan ID')}
              value={vision.visionId ?? '-'}
            />
          </Grid>
          <Grid size={{ xs: 6 }}>
            <LabelizedField
              label={t('Funds Commitment Number')}
              value={vision.fcNum ?? '-'}
            />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
    </Box>
  );
}
