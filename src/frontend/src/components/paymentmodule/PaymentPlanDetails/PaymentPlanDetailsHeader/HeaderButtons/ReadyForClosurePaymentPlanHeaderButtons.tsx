import { Box, Button } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingButton } from '../../../../core/LoadingButton';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { showApiErrorMessages } from '@utils/utils';
import { PERMISSIONS } from 'src/config/permissions';
import { ClosePaymentPlanDialog } from '../ClosePaymentPlanDialog';

export interface ReadyForClosurePaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canSendBack: boolean;
  canClose: boolean;
}

export function ReadyForClosurePaymentPlanHeaderButtons({
  paymentPlan,
  canSendBack,
  canClose,
}: ReadyForClosurePaymentPlanHeaderButtonsProps): ReactElement {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [closeDialogOpen, setCloseDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();

  const { mutateAsync: sendBack, isPending: loadingSendBack } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansSendBackToFinishedRetrieve(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: paymentPlan.id,
        },
      ),
    onSuccess: () => {
      showMessage(t('Payment Plan has been sent back.'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const shouldDisableDownloadXlsx = !paymentPlan.canDownloadXlsx;

  return (
    <Box display="flex" alignItems="center">
      <>
        {paymentPlan.hasPaymentListExportFile && (
          <Box m={2}>
            <Button
              color="primary"
              component="a"
              variant="contained"
              data-cy="button-download-xlsx"
              download
              href={`/api/download-payment-plan-payment-list/${paymentPlan.id}`}
              disabled={shouldDisableDownloadXlsx}
              data-perm={PERMISSIONS.PM_DOWNLOAD_XLSX_FOR_FSP}
            >
              {t('Download XLSX')}
            </Button>
          </Box>
        )}

        {canSendBack && (
          <Box m={2}>
            <LoadingButton
              color="primary"
              variant="contained"
              data-cy="button-send-back"
              onClick={() => sendBack()}
              loading={loadingSendBack}
              data-perm={PERMISSIONS.PM_MARK_READY_FOR_CLOSURE}
            >
              {t('Send Back')}
            </LoadingButton>
          </Box>
        )}

        {canClose && (
          <Box m={2}>
            <Button
              color="primary"
              variant="contained"
              data-cy="button-close"
              onClick={() => setCloseDialogOpen(true)}
              data-perm={PERMISSIONS.PM_CLOSE_FINISHED}
            >
              {t('Close')}
            </Button>
          </Box>
        )}
        <ClosePaymentPlanDialog
          paymentPlan={paymentPlan}
          open={closeDialogOpen}
          onClose={() => setCloseDialogOpen(false)}
        />
      </>
    </Box>
  );
}
