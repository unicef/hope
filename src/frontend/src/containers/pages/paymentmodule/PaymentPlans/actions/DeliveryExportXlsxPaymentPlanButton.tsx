import { usePermissions } from '@hooks/usePermissions';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanDetail } from '../types';
import { isPaymentPlanBackgroundActionBusy } from '../utils';
import { PaymentPlanExportXlsxDialog } from './PaymentPlanExportXlsxDialog';

interface DeliveryExportXlsxPaymentPlanButtonProps {
  paymentPlan: PaymentPlanDetail | null;
}

export function DeliveryExportXlsxPaymentPlanButton({
  paymentPlan,
}: DeliveryExportXlsxPaymentPlanButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const permissions = usePermissions();

  if (!hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_EXPORT_XLSX, permissions))
    return null;
  if (paymentPlan && !paymentPlan.canExport && !paymentPlan.canRegenerateExport)
    return null;
  const label = paymentPlan?.canRegenerateExport ? t('Re-export') : t('Export');

  return (
    <PaymentPlanExportXlsxDialog
      paymentPlanId={paymentPlan?.id ?? ''}
      showTemplateChoice={false}
      buttonLabel={label}
      dialogTitle={label}
      buttonVariant="contained"
      disabled={!paymentPlan || isPaymentPlanBackgroundActionBusy(paymentPlan)}
      dataCySuffix="delivery-export-xlsx-group"
    />
  );
}
