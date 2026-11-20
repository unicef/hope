import { usePermissions } from '@hooks/usePermissions';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanDetail } from '../types';
import { isPaymentPlanBackgroundActionBusy } from '../utils';
import { PaymentPlanExportXlsxDialog } from './PaymentPlanExportXlsxDialog';

interface DeliveryExportXlsxWithAuthCodePaymentPlanButtonProps {
  paymentPlan: PaymentPlanDetail | null;
}

export function DeliveryExportXlsxWithAuthCodePaymentPlanButton({
  paymentPlan,
}: DeliveryExportXlsxWithAuthCodePaymentPlanButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const permissions = usePermissions();

  if (
    !hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_EXPORT_XLSX, permissions) ||
    !hasPermissions(PERMISSIONS.PM_DOWNLOAD_FSP_AUTH_CODE, permissions)
  )
    return null;
  if (paymentPlan && !paymentPlan.canExport && !paymentPlan.canRegenerateExport)
    return null;
  const label = paymentPlan?.canRegenerateExport ? t('Re-export') : t('Export');

  return (
    <PaymentPlanExportXlsxDialog
      paymentPlanId={paymentPlan?.id ?? ''}
      buttonLabel={`${label} ${t('with Auth Code')}`}
      dialogTitle={`${label} ${t('with Auth Code')}`}
      buttonVariant="outlined"
      disabled={!paymentPlan || isPaymentPlanBackgroundActionBusy(paymentPlan)}
      dataCySuffix="delivery-export-xlsx-with-auth-code-group"
    />
  );
}
