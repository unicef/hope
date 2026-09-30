import { useConfirmation } from '@components/core/ConfirmationDialog/useConfirmation';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanGroupDetail } from '../types';

interface LockUnlockGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function LockUnlockGroupButton({
  group,
}: LockUnlockGroupButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
  const queryClient = useQueryClient();
  const permissions = usePermissions();

  const isLocked = group?.status === PaymentPlanGroupStatusEnum.LOCKED;
  const { mutateAsync, isPending } = useMutation({
    mutationFn: () => {
      const params = {
        businessAreaSlug: businessArea,
        programCode: programId,
        id: group?.id ?? '',
      };
      return isLocked
        ? RestService.restBusinessAreasProgramsPaymentPlanGroupsUnlockCreate(
            params,
          )
        : RestService.restBusinessAreasProgramsPaymentPlanGroupsLockCreate(
            params,
          );
    },
    onSuccess: async () => {
      showMessage(isLocked ? t('Group unlocked') : t('Group locked'));
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

  if (!group) return null;
  if (!hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP, permissions))
    return null;
  if (
    group.status !== PaymentPlanGroupStatusEnum.OPEN &&
    group.status !== PaymentPlanGroupStatusEnum.LOCKED
  )
    return null;

  const handleClick = (): void => {
    confirm({
      title: isLocked ? t('Unlock Group') : t('Lock Group'),
      content: isLocked
        ? t(
            'The group will accept new Payment Plans again and the FSP of its Payment Plans will be unlocked.',
          )
        : t(
            'No new Payment Plans can be added to the group and the FSP of its Payment Plans will be locked.',
          ),
      continueText: isLocked ? t('Unlock') : t('Lock'),
    }).then(() => mutateAsync().catch(() => undefined));
  };

  return (
    <Box sx={{ p: 2 }}>
      <LoadingButton
        loading={isPending}
        variant={isLocked ? 'outlined' : 'contained'}
        color="primary"
        onClick={handleClick}
        data-cy={isLocked ? 'button-unlock-group' : 'button-lock-group'}
      >
        {isLocked ? t('Unlock') : t('Lock')}
      </LoadingButton>
    </Box>
  );
}
