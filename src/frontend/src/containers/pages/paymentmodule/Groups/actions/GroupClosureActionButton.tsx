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
import type { PaymentPlanGroupDetail } from '../types';

export type GroupClosureAction = 'reactivate' | 'readyForClosure' | 'sendBack';

type GroupRequestParams = Parameters<
  typeof RestService.restBusinessAreasProgramsPaymentPlanGroupsReactivateAbortCreate
>[0];

interface ActionConfig {
  request: (params: GroupRequestParams) => Promise<unknown>;
  label: string;
  successMessage: string;
  dataCy: string;
  permission: string;
}

const ACTIONS: Record<GroupClosureAction, ActionConfig> = {
  reactivate: {
    request: (params) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsReactivateAbortCreate(
        params,
      ),
    label: 'Reactivate',
    successMessage: 'Payment Plan has been reactivated.',
    dataCy: 'button-reactivate-payment-plan-group',
    permission: PERMISSIONS.PM_REACTIVATE_ABORT,
  },
  readyForClosure: {
    request: (params) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsReadyForClosureCreate(
        params,
      ),
    label: 'Set Ready for Closure',
    successMessage: 'Payment Plan marked as ready for closure.',
    dataCy: 'button-set-ready-for-closure',
    permission: PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
  },
  sendBack: {
    request: (params) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsSendBackToFinishedCreate(
        params,
      ),
    label: 'Send Back',
    successMessage: 'Payment Plan has been sent back.',
    dataCy: 'button-send-back',
    permission: PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
  },
};

interface GroupClosureActionButtonProps {
  group: PaymentPlanGroupDetail;
  action: GroupClosureAction;
}

export function GroupClosureActionButton({
  group,
  action,
}: GroupClosureActionButtonProps): ReactElement {
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
        id: group.id,
      }),
    onSuccess: async () => {
      showMessage(t(config.successMessage));
      await Promise.all(
        [
          RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
          RestService.restBusinessAreasProgramsPaymentPlanGroupsList,
          RestService.restBusinessAreasProgramsPaymentPlansList,
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
