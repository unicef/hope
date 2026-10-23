import { MarkAsReleasedPaymentPlan } from '../MarkAsReleasedPaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';
import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { AbortPaymentPlan } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/AbortPaymentPlan';
import { HeaderActions } from '@core/HeaderActions';

export interface InReviewPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canReject: boolean;
  canMarkAsReleased: boolean;
  canAbort: boolean;
}

export function InReviewPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canMarkAsReleased,
  canAbort,
}: InReviewPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <HeaderActions spacing="none">
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canMarkAsReleased && !paymentPlan.visionManaged && (
        <MarkAsReleasedPaymentPlan paymentPlan={paymentPlan} />
      )}
      {canAbort && <AbortPaymentPlan paymentPlan={paymentPlan} />}
    </HeaderActions>
  );
}
