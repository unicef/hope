import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Button } from '@mui/material';
import { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { useProgramContext } from '../../../../../programContext';
import type { PaymentPlanGroupDetail } from '../types';

// Mirrors PaymentPlanGroup.SUMMARY_PDF_STATUSES on the backend.
const SUMMARY_PDF_STATUSES: string[] = [
  PaymentPlanGroupStatusEnum.IN_REVIEW,
  PaymentPlanGroupStatusEnum.ACCEPTED,
  PaymentPlanGroupStatusEnum.FINISHED,
];

interface ExportGroupSummaryPdfButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function ExportGroupSummaryPdfButton({
  group,
}: ExportGroupSummaryPdfButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const queryClient = useQueryClient();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();

  const { mutate: exportPdf, isPending } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsExportPdfPaymentPlanSummaryRetrieve(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: group?.id,
        },
      ),
    onSuccess: () => {
      showMessage(t('Payment Plan Summary is being generated.'));
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
        ),
      });
    },
    onError: (error) => {
      showApiErrorMessages(error, showMessage, t('Failed to generate PDF.'));
    },
  });

  if (!group?.status) return null;
  if (!hasPermissions(PERMISSIONS.PM_EXPORT_PDF_SUMMARY, permissions))
    return null;
  const canGenerate = SUMMARY_PDF_STATUSES.includes(group.status);
  if (!canGenerate && !group.exportPdfFileSummary) return null;

  return (
    <Box sx={{ display: 'flex', gap: 2 }}>
      {group.exportPdfFileSummary && (
        <Button
          color="primary"
          variant="outlined"
          component="a"
          href={group.exportPdfFileSummary}
          download
          data-cy="button-download-group-summary-pdf"
        >
          {t('Download Payment Plan Summary')}
        </Button>
      )}
      {canGenerate && (
        <LoadingButton
          loading={isPending}
          color="primary"
          variant="contained"
          onClick={() => exportPdf()}
          disabled={!isActiveProgram}
          data-cy="button-export-group-summary-pdf"
          data-perm={PERMISSIONS.PM_EXPORT_PDF_SUMMARY}
        >
          {group.exportPdfFileSummary
            ? t('Regenerate Payment Plan Summary')
            : t('Generate Payment Plan Summary')}
        </LoadingButton>
      )}
    </Box>
  );
}
