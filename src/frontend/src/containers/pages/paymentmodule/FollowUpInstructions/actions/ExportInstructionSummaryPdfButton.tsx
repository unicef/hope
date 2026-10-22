import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Button } from '@mui/material';
import type { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { useProgramContext } from '../../../../../programContext';

// Mirrors FollowUpInstruction.SUMMARY_PDF_STATUSES on the backend.
const SUMMARY_PDF_STATUSES = ['IN_REVIEW', 'ACCEPTED', 'FINISHED'];

interface ExportInstructionSummaryPdfButtonProps {
  instruction: FollowUpInstructionDetail;
}

export function ExportInstructionSummaryPdfButton({
  instruction,
}: ExportInstructionSummaryPdfButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const queryClient = useQueryClient();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();

  const { mutate: exportPdf, isPending } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsFollowUpInstructionsExportPdfPaymentPlanSummaryRetrieve(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: instruction.id,
        },
      ),
    onSuccess: () => {
      showMessage(t('Payment Plan Summary is being generated.'));
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsFollowUpInstructionsRetrieve,
        ),
      });
    },
    onError: (error) => {
      showApiErrorMessages(error, showMessage, t('Failed to generate PDF.'));
    },
  });

  if (!instruction.status) return null;
  if (!hasPermissions(PERMISSIONS.PM_EXPORT_PDF_SUMMARY, permissions))
    return null;
  const canGenerate = SUMMARY_PDF_STATUSES.includes(instruction.status);
  if (!canGenerate && !instruction.exportPdfFileSummary) return null;

  return (
    <Box sx={{ display: 'flex', gap: 2 }}>
      {instruction.exportPdfFileSummary && (
        <Button
          color="primary"
          variant="outlined"
          component="a"
          href={instruction.exportPdfFileSummary}
          download
          data-cy="button-download-instruction-summary-pdf"
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
          data-cy="button-export-instruction-summary-pdf"
          data-perm={PERMISSIONS.PM_EXPORT_PDF_SUMMARY}
        >
          {instruction.exportPdfFileSummary
            ? t('Regenerate Payment Plan Summary')
            : t('Generate Payment Plan Summary')}
        </LoadingButton>
      )}
    </Box>
  );
}
