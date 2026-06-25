import { Box } from '@mui/material';
import { CreateChildPaymentPlan } from '../../../CreateChildPaymentPlan';
import { SplitIntoPaymentLists } from '../SplitIntoPaymentLists';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

export interface AcceptedPaymentPlanHeaderButtonsProps {
  canSplit: boolean;
  paymentPlan: PaymentPlanDetail;
  isInstructionManaged?: boolean;
}

export function AcceptedPaymentPlanHeaderButtons({
  canSplit,
  paymentPlan,
  isInstructionManaged = false,
}: AcceptedPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <Box display="flex" alignItems="center">
      <>
        {paymentPlan.canCreateFollowUp && (
          <Box p={2}>
            <CreateChildPaymentPlan paymentPlan={paymentPlan} variant="followup" />
          </Box>
        )}
        {paymentPlan.canCreateTopUp && (
          <Box p={2}>
            <CreateChildPaymentPlan paymentPlan={paymentPlan} variant="topup" />
          </Box>
        )}
        {paymentPlan.canCreateTopUpAmendment && (
          <Box p={2}>
            <CreateChildPaymentPlan
              paymentPlan={paymentPlan}
              variant="amendment"
            />
          </Box>
        )}
        {!isInstructionManaged && (
          <Box p={2}>
            <SplitIntoPaymentLists
              paymentPlan={paymentPlan}
              canSplit={canSplit}
            />
          </Box>
        )}
        {/* Close moved to the Ready for Closure flow; Send Xlsx Password and Send to FSP moved to the Group / Batch detail pages. */}
      </>
    </Box>
  );
}
