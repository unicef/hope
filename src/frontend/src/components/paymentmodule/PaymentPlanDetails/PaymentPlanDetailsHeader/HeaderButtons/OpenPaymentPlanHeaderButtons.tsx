import { Box } from '@mui/material';
import { DeletePaymentPlan } from '../DeletePaymentPlan';
import { LockPaymentPlan } from '../LockPaymentPlan';
import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

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
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
      }}
    >
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
    </Box>
  );
}
