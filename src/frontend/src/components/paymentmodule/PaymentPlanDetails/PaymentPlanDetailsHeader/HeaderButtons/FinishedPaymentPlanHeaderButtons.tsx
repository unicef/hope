import { Box, Button } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingButton } from '../../../../core/LoadingButton';
import { CreateChildPaymentPlan } from '../../../CreateChildPaymentPlan';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { SplitIntoPaymentLists } from '../SplitIntoPaymentLists';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { showApiErrorMessages } from '@utils/utils';
import { PERMISSIONS } from 'src/config/permissions';

export interface FinishedPaymentPlanHeaderButtonsProps {
  canSendToPaymentGateway: boolean;
  canSplit: boolean;
  paymentPlan: PaymentPlanDetail;
  canMarkReadyForClosure: boolean;
}

export function FinishedPaymentPlanHeaderButtons({
  canSendToPaymentGateway,
  canSplit,
  paymentPlan,
  canMarkReadyForClosure,
}: FinishedPaymentPlanHeaderButtonsProps): ReactElement {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();

  const { mutateAsync: markReadyForClosure, isPending: loadingReadyForClosure } =
    useMutation({
      mutationFn: () =>
        RestService.restBusinessAreasProgramsPaymentPlansReadyForClosureRetrieve(
          {
            businessAreaSlug: businessArea,
            programCode: programId,
            id: paymentPlan.id,
          },
        ),
      onSuccess: () => {
        showMessage(t('Payment Plan marked as ready for closure.'));
        queryClient.invalidateQueries({
          queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
        });
      },
      onError: (error: any) => {
        showApiErrorMessages(error, showMessage);
      },
    });

  const {
    mutateAsync: sendToPaymentGateway,
    isPending: LoadingSendToPaymentGateway,
  } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansSendToPaymentGatewayRetrieve(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: paymentPlan.id,
        },
      ),
    onSuccess: () => {
      showMessage(t('Sending to Payment Gateway started'));
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const shouldDisableDownloadXlsx = !paymentPlan.canDownloadXlsx;

  return (
    <Box display="flex" alignItems="center">
      <>
        {paymentPlan.canCreateFollowUp && (
          <Box p={2}>
            <CreateChildPaymentPlan paymentPlan={paymentPlan} variant="followup" />
          </Box>
        )}
        <Box p={2}>
          <SplitIntoPaymentLists paymentPlan={paymentPlan} canSplit={canSplit} />
        </Box>
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

        {canSendToPaymentGateway && (
          <Box m={2}>
            <Button
              type="button"
              color="primary"
              variant="contained"
              onClick={() => sendToPaymentGateway()}
              data-cy="button-send-to-payment-gateway"
              disabled={LoadingSendToPaymentGateway}
              data-perm={PERMISSIONS.PM_SEND_TO_PAYMENT_GATEWAY}
            >
              {t('Send to FSP')}
            </Button>
          </Box>
        )}

        {canMarkReadyForClosure && (
          <Box m={2}>
            <LoadingButton
              color="primary"
              variant="contained"
              data-cy="button-set-ready-for-closure"
              onClick={() => markReadyForClosure()}
              loading={loadingReadyForClosure}
              data-perm={PERMISSIONS.PM_MARK_READY_FOR_CLOSURE}
            >
              {t('Set Ready for Closure')}
            </LoadingButton>
          </Box>
        )}
      </>
    </Box>
  );
}
