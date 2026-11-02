import { AuthorizePaymentPlan } from '../AuthorizePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';
import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { AbortPaymentPlan } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/AbortPaymentPlan';
import { HeaderActions } from '@core/HeaderActions';

export interface InAuthorizationPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canReject: boolean;
  canAuthorize: boolean;
  canAbort: boolean;
}

export function InAuthorizationPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canAuthorize,
  canAbort,
}: InAuthorizationPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <HeaderActions spacing="none">
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canAuthorize && <AuthorizePaymentPlan paymentPlan={paymentPlan} />}
      {canAbort && <AbortPaymentPlan paymentPlan={paymentPlan} />}
    </HeaderActions>
  );
}
