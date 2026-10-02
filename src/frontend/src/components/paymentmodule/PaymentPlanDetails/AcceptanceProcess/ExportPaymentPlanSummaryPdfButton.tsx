import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingButton } from '@core/LoadingButton';
import { useProgramContext } from '../../../../programContext';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';

const EXPORTABLE_STATUSES: string[] = [
  PaymentPlanStatusEnum.ACCEPTED,
  PaymentPlanStatusEnum.FINISHED,
  PaymentPlanStatusEnum.IN_REVIEW,
  PaymentPlanStatusEnum.READY_FOR_CLOSURE,
  PaymentPlanStatusEnum.CLOSED,
];

interface ExportPaymentPlanSummaryPdfButtonProps {
  paymentPlan: PaymentPlanDetail;
}

export function ExportPaymentPlanSummaryPdfButton({
  paymentPlan,
}: ExportPaymentPlanSummaryPdfButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId: programCode } = useBaseUrl();

  const exportPdfMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansExportPdfPaymentPlanSummaryRetrieve(
        {
          businessAreaSlug: businessArea,
          programCode: programCode,
          id: paymentPlan.id,
        },
      ),
  });

  if (
    !hasPermissions(PERMISSIONS.PM_EXPORT_PDF_SUMMARY, permissions) ||
    !EXPORTABLE_STATUSES.includes(paymentPlan.status)
  ) {
    return null;
  }

  const handleExportPdf = async (): Promise<void> => {
    try {
      await exportPdfMutation.mutateAsync();
      showMessage(t('PDF generated. Please check your email.'));
    } catch (e) {
      showApiErrorMessages(e, showMessage, t('Failed to generate PDF.'));
    }
  };

  return (
    <LoadingButton
      loading={exportPdfMutation.isPending}
      color="primary"
      variant="contained"
      onClick={handleExportPdf}
      disabled={!isActiveProgram}
      data-perm={PERMISSIONS.PM_EXPORT_PDF_SUMMARY}
    >
      {t('Download Payment Plan Summary')}
    </LoadingButton>
  );
}
