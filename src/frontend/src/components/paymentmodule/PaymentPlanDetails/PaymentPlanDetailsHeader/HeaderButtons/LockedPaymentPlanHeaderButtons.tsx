import { Box } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';
import { useSnackbar } from '@hooks/useSnackBar';
import { Action, PaymentPlanQuery } from '@generated/graphql';
import { LoadingButton } from '@core/LoadingButton';
import { LockFspPaymentPlan } from '../LockFspPaymentPlan';
import { useProgramContext } from '../../../../../programContext';

export interface LockedPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canUnlock: boolean;
  permissions: string[];
}

export function LockedPaymentPlanHeaderButtons({
  paymentPlan,
  canUnlock,
  permissions,
}: LockedPaymentPlanHeaderButtonsProps): React.ReactElement {
  const { t } = useTranslation();
  const { id } = paymentPlan;
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();

  const { mutatePaymentPlanAction: unlock, loading: loadingUnlock } =
    usePaymentPlanAction(Action.Unlock, id, () =>
      showMessage(t('Payment Plan has been unlocked.')),
    );

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
            data-cy="button-unlock-payment-plan"
          >
            {t('Unlock')}
          </LoadingButton>
        </Box>
      )}
      <LockFspPaymentPlan paymentPlan={paymentPlan} permissions={permissions} />
    </Box>
  );
}
