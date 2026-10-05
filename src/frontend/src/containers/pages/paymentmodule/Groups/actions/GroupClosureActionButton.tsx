import { LoadingButton } from '@core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from '../../../../../programContext';
import type { PaymentPlanGroupDetail } from '../types';

export type GroupClosureAction = 'reactivate' | 'readyForClosure' | 'sendBack';

interface ActionConfig {
  label: string;
  successMessage: string;
  dataCy: string;
  permission: string;
}

const ACTIONS: Record<GroupClosureAction, ActionConfig> = {
  reactivate: {
    label: 'Reactivate',
    successMessage: 'Payment Plan Group has been reactivated.',
    dataCy: 'button-reactivate-payment-plan-group',
    permission: PERMISSIONS.PM_REACTIVATE_ABORT,
  },
  readyForClosure: {
    label: 'Set Ready for Closure',
    successMessage: 'Payment Plan Group marked as ready for closure.',
    dataCy: 'button-set-ready-for-closure',
    permission: PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
  },
  sendBack: {
    label: 'Send Back',
    successMessage: 'Payment Plan Group has been sent back.',
    dataCy: 'button-send-back',
    permission: PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
  },
};

interface GroupClosureActionButtonProps {
  group: PaymentPlanGroupDetail;
  action: GroupClosureAction;
}

export function GroupClosureActionButton({
  action,
}: GroupClosureActionButtonProps): ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const config = ACTIONS[action];

  const { mutate, isPending } = useMutation({
    // TODO: call the group endpoint for this action (reactivate-abort,
    // ready-for-closure, send-back-to-finished) with id: group.id once the backend adds it.
    mutationFn: () => Promise.reject(new Error(t('Not available yet'))),
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
    onError: (error) => showMessage(error.message),
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
