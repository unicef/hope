import { usePermissions } from '@hooks/usePermissions';
import { GetApp } from '@mui/icons-material';
import { Box, Button } from '@mui/material';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanDetail } from '../types';

interface DownloadPaymentPlanXlsxButtonProps {
  paymentPlan: PaymentPlanDetail | null;
}

export function DownloadPaymentPlanXlsxButton({
  paymentPlan,
}: DownloadPaymentPlanXlsxButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const permissions = usePermissions();

  if (!hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_EXPORT_XLSX, permissions))
    return null;

  if (!paymentPlan?.exportFileDelivery) return null;
  const href = paymentPlan.exportFileDelivery;

  return (
    <Box
      sx={{
        m: 2,
      }}
    >
      <Button
        component="a"
        href={href}
        download
        startIcon={<GetApp />}
        color="primary"
        variant="outlined"
        data-cy="button-download-group-xlsx"
      >
        {t('Download XLSX')}
      </Button>
    </Box>
  );
}
