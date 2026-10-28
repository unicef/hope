import { Box } from '@mui/material';
import { DeletePaymentPlan } from '../DeletePaymentPlan';
import { LockPaymentPlan } from '../LockPaymentPlan';
import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { HeaderActions } from '@core/HeaderActions';

export interface OpenPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canRemove: boolean;
  canLock: boolean;
}

export function OpenPaymentPlanHeaderButtons({
  paymentPlan,
  canRemove,
  canLock,
}: OpenPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <HeaderActions spacing="none">
      {canRemove && <DeletePaymentPlan paymentPlan={paymentPlan} />}
      {canLock && (
        <Box
          sx={{
            m: 2,
          }}
        >
          <LockPaymentPlan paymentPlan={paymentPlan} />
        </Box>
      )}
    </HeaderActions>
  );
}
