import React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { PaymentPlanDetails } from './PaymentPlanDetails';
import { fakeBaseUrl } from '../../../../../fixtures/core/fakeBaseUrl';

describe('components/paymentmodule/PaymentPlanDetails/PaymentPlanDetails', () => {
  it('should render', () => {
    const { container } = render(
      <PaymentPlanDetails
        baseUrl={fakeBaseUrl}
        paymentPlan={fakeApolloPaymentPlan}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
