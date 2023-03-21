import React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { PaymentPlanDetails } from './PaymentPlanDetails';

describe('components/paymentmodule/PaymentPlanDetails/PaymentPlanDetails', () => {
  it('should render', () => {
    const { container } = render(
      <PaymentPlanDetails
        businessArea='afghanistan'
        paymentPlan={fakeApolloPaymentPlan}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
