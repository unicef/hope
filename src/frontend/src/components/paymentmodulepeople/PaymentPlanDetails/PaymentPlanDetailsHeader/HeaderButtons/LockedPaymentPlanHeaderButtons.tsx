import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingButton } from '@core/LoadingButton';
import { LockFspPaymentPlan } from '../LockFspPaymentPlan';
import { useProgramContext } from '../../../../../programContext';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { AbortPaymentPlan } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/AbortPaymentPlan';

export interface LockedPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canUnlock: boolean;
  permissions: string[];
  canAbort: boolean;
}

export function LockedPaymentPlanHeaderButtons({
  paymentPlan,
  canUnlock,
  permissions,
  canAbort,
}: LockedPaymentPlanHeaderButtonsProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();

  const { mutateAsync: unlock, isPending: loadingUnlock } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansUnlockRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: paymentPlan.id,
      }),
    onSuccess: async () => {
      showMessage(t('Payment Plan has been unlocked.'));
      await queryClient.invalidateQueries({
        queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
        exact: false,
      });
    },
    onError: (error) => {
      showApiErrorMessages(error, showMessage);
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
          >
            {t('Unlock')}
          </LoadingButton>
        </Box>
      )}
      <LockFspPaymentPlan paymentPlan={paymentPlan} permissions={permissions} />
      {canAbort && (
        <Box m={2}>
          <AbortPaymentPlan paymentPlan={paymentPlan} />
        </Box>
      )}
    </Box>
  );
}
