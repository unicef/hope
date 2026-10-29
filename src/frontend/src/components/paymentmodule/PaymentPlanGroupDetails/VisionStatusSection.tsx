import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { Alert, Box, Typography } from '@mui/material';
import type { PaymentPlanGroupDetail } from '@restgenerated/models/PaymentPlanGroupDetail';
import { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  responsiveValue,
  ResponsiveGrid,
  ResponsiveGridContainer,
} from 'src/responsive';

const errorStatuses = new Set([
  'SEND_FAILED',
  'CALLBACK_FAILED',
  'FC_NOT_FOUND',
]);

export function VisionStatusSection({
  group,
}: {
  group: PaymentPlanGroupDetail;
}): ReactElement | null {
  const { t } = useTranslation();
  if (
    group.vision.status === 'NOT_SENT' &&
    (!group.visionManaged ||
      group.status !== PaymentPlanGroupStatusEnum.IN_REVIEW)
  ) {
    return null;
  }

  const vision = group.vision;
  const severity = errorStatuses.has(vision.status)
    ? 'error'
    : vision.status === 'FC_ASSOCIATED' || vision.status === 'RELEASED'
      ? 'success'
      : 'info';

  return (
    <Box sx={{ m: responsiveValue(2, 5) }}>
      <ContainerColumnWithBorder>
        <Box sx={{ mt: 4 }}>
          <Title>
            <Typography variant="h6">{t('Vision Integration')}</Typography>
          </Title>
        </Box>
        <Alert severity={severity} sx={{ mb: 3 }}>
          {t(vision.status.replaceAll('_', ' '))}
          {vision.errorCode
            ? `: ${t(vision.errorCode.replaceAll('_', ' '))}`
            : ''}
        </Alert>
        <ResponsiveGridContainer spacing={3}>
          <ResponsiveGrid size="half">
            <LabelizedField
              label={t('Vision Payment Plan ID')}
              value={vision.visionId ?? '-'}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="half">
            <LabelizedField
              label={t('Funds Commitment Numbers')}
              value={
                vision.fcNumbers.length ? vision.fcNumbers.join(', ') : '-'
              }
            />
          </ResponsiveGrid>
        </ResponsiveGridContainer>
      </ContainerColumnWithBorder>
    </Box>
  );
}
