import { useConfirmation } from '@components/core/ConfirmationDialog/useConfirmation';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanDetail } from '../types';

interface LockUnlockPaymentPlanButtonProps {
  paymentPlan: PaymentPlanDetail | null;
}

export function LockUnlockPaymentPlanButton({
  paymentPlan,
}: LockUnlockPaymentPlanButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
  const queryClient = useQueryClient();
  const permissions = usePermissions();

  const isLocked = paymentPlan?.status === PaymentPlanStatusEnum.LOCKED;
  const { mutateAsync, isPending } = useMutation({
    mutationFn: () => {
      const params = {
        businessAreaSlug: businessArea,
        programCode: programId,
        id: paymentPlan?.id ?? '',
      };
      return isLocked
        ? RestService.restBusinessAreasProgramsPaymentPlansUnlockCreate(params)
        : RestService.restBusinessAreasProgramsPaymentPlansLockCreate(params);
    },
    onSuccess: async () => {
      showMessage(
        isLocked ? t('Payment Plan unlocked') : t('Payment Plan locked'),
      );
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

  if (!paymentPlan) return null;
  if (!hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP, permissions))
    return null;
  if (
    paymentPlan.status !== PaymentPlanStatusEnum.OPEN &&
    paymentPlan.status !== PaymentPlanStatusEnum.LOCKED
  )
    return null;

  const handleClick = (): void => {
    confirm({
      title: isLocked ? t('Unlock Payment Plan') : t('Lock Payment Plan'),
      content: isLocked
        ? t(
            'The payment plan will accept new Payment Lists again and the FSP of its Payment Lists will be unlocked.',
          )
        : t(
            'No new Payment Lists can be added to the payment plan and the FSP of its Payment Lists will be locked.',
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
