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
import { PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from '../../../../../programContext';
import type { PaymentPlanDetail } from '../types';

export type PaymentPlanClosureAction =
  'reactivate' | 'readyForClosure' | 'sendBack';

type PaymentPlanRequestParams = Parameters<
  typeof RestService.restBusinessAreasProgramsPaymentPlansReactivateAbortCreate
>[0];

interface ActionConfig {
  request: (params: PaymentPlanRequestParams) => Promise<unknown>;
  label: string;
  successMessage: string;
  dataCy: string;
  permission: string;
}

const ACTIONS: Record<PaymentPlanClosureAction, ActionConfig> = {
  reactivate: {
    request: (params) =>
      RestService.restBusinessAreasProgramsPaymentPlansReactivateAbortCreate(
        params,
      ),
    label: 'Reactivate',
    successMessage: 'Payment Plan has been reactivated.',
    dataCy: 'button-reactivate-payment-plan',
    permission: PERMISSIONS.PM_REACTIVATE_ABORT,
  },
  readyForClosure: {
    request: (params) =>
      RestService.restBusinessAreasProgramsPaymentPlansReadyForClosureCreate(
        params,
      ),
    label: 'Set Ready for Closure',
    successMessage: 'Payment Plan marked as ready for closure.',
    dataCy: 'button-set-ready-for-closure',
    permission: PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
  },
  sendBack: {
    request: (params) =>
      RestService.restBusinessAreasProgramsPaymentPlansSendBackToFinishedCreate(
        params,
      ),
    label: 'Send Back',
    successMessage: 'Payment Plan has been sent back.',
    dataCy: 'button-send-back',
    permission: PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
  },
};

interface PaymentPlanClosureActionButtonProps {
  paymentPlan: PaymentPlanDetail;
  action: PaymentPlanClosureAction;
}

export function PaymentPlanClosureActionButton({
  paymentPlan,
  action,
}: PaymentPlanClosureActionButtonProps): ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const config = ACTIONS[action];

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      config.request({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: paymentPlan.id,
      }),
    onSuccess: async () => {
      showMessage(t(config.successMessage));
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
    <Box sx={{ m: 2 }}>
      <LoadingButton
        color="primary"
        variant="contained"
        onClick={() => mutate()}
        loading={isPending}
        disabled={!isActiveProgram}
        data-cy={config.dataCy}
        data-perm={config.permission}
      >
        {t(config.label)}
      </LoadingButton>
    </Box>
  );
}
