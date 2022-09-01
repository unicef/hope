import React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/payments/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { AcceptanceProcess } from './AcceptanceProcess';

describe('components/paymentmodule/PaymentPlanDetails/AcceptanceProcess', () => {
  it('should render', () => {
    const { container } = render(
      <AcceptanceProcess paymentPlan={fakeApolloPaymentPlan} />,
    );
    expect(container).toMatchSnapshot();
  });

  it('should render empty without Approval Process', () => {
    const { container } = render(
      <AcceptanceProcess paymentPlan={{...fakeApolloPaymentPlan, approvalProcess: {...fakeApolloPaymentPlan.approvalProcess, edges: []}}} />,
    );
    expect(container).toMatchSnapshot();
  });
});
