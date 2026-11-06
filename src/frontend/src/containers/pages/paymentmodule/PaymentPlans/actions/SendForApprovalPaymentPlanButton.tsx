import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from '../../../../../programContext';
import type { PaymentPlanDetail } from '../types';

interface SendForApprovalPaymentPlanButtonProps {
  paymentPlan: PaymentPlanDetail;
}

export function SendForApprovalPaymentPlanButton({
  paymentPlan,
}: SendForApprovalPaymentPlanButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const queryClient = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansSendForApprovalCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: paymentPlan.id,
      }),
    onSuccess: async () => {
      showMessage(t('Payment Plan has been sent for approval.'));
      await Promise.all(
        [
          RestService.restBusinessAreasProgramsPaymentPlansRetrieve,
          RestService.restBusinessAreasProgramsPaymentPlansList,
          RestService.restBusinessAreasProgramsPaymentListsList,
        ].map((fn) =>
          queryClient.invalidateQueries({ queryKey: restQueryKey(fn) }),
        ),
      );
    },
    onError: (error) => showApiErrorMessages(error, showMessage),
  });

  return (
    <Box sx={{ p: 2 }}>
      <LoadingButton
        loading={isPending}
        variant="contained"
        color="primary"
        onClick={() => mutate()}
        disabled={!isActiveProgram}
        data-cy="button-send-for-approval"
      >
        {t('Send For Approval')}
      </LoadingButton>
    </Box>
  );
}
