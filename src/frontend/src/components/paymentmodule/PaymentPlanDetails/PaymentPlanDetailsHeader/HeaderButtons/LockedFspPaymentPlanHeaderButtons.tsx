import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingButton } from '@core/LoadingButton';
import { useProgramContext } from '../../../../../programContext';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';

export interface LockedFspPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canUnlock: boolean;
  canSendForApproval: boolean;
}

export function LockedFspPaymentPlanHeaderButtons({
  paymentPlan,
  canUnlock,
  canSendForApproval,
}: LockedFspPaymentPlanHeaderButtonsProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();

  const { mutateAsync: unlock, isPending: loadingUnlock } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansUnlockFspRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: paymentPlan.id,
      }),
    onSuccess: async () => {
      showMessage(t('Payment Plan FSPs have been unlocked.'));
      await queryClient.invalidateQueries({
        queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
        exact: false,
      });
    },
    onError: (error) => {
      showMessage(error.message || t('An error occurred while unlocking FSP'));
    },
  });

  const { mutateAsync: sendForApproval, isPending: loadingSendForApproval } =
    useMutation({
      mutationFn: () =>
        RestService.restBusinessAreasProgramsPaymentPlansSendForApprovalRetrieve(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            id: paymentPlan.id,
          },
        ),
      onSuccess: async () => {
        showMessage(t('Payment Plan has been sent for approval.'));
        await queryClient.invalidateQueries({
          queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
          exact: false,
        });
      },
      onError: (error) => {
        showMessage(
          error.message || t('An error occurred while sending for approval'),
        );
      },
    });

  return (
    <Box display="flex" alignItems="center">
      {canUnlock && (
        <Box m={2}>
          <LoadingButton
            loading={loadingUnlock}
            variant="outlined"
            color="primary"
            onClick={() => unlock()}
            disabled={!isActiveProgram}
            data-cy="button-unlock-fsp"
          >
            {t('Unlock FSP')}
          </LoadingButton>
        </Box>
      )}
      {canSendForApproval && (
        <Box m={2}>
          <LoadingButton
            loading={loadingSendForApproval}
            variant="contained"
            color="primary"
            onClick={() => sendForApproval()}
            data-cy="button-send-for-approval"
            disabled={!isActiveProgram}
          >
            {t('Send For Approval')}
          </LoadingButton>
        </Box>
      )}
    </Box>
  );
}
