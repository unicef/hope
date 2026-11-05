import { ApprovePaymentPlan } from '../ApprovePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';
import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { AbortPaymentPlan } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/AbortPaymentPlan';
import { HeaderActions } from '@core/HeaderActions';

export interface InApprovalPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canReject: boolean;
  canApprove: boolean;
  canAbort: boolean;
}

export function InApprovalPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canApprove,
  canAbort,
}: InApprovalPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <HeaderActions spacing="none">
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canApprove && <ApprovePaymentPlan paymentPlan={paymentPlan} />}
      {canAbort && <AbortPaymentPlan paymentPlan={paymentPlan} />}
    </HeaderActions>
  );
}
