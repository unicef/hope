import React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/payments/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { FspSection } from './FspSection';

describe('components/paymentmodule/PaymentPlanDetails/FspSection', () => {
  it('should render Set Up FSP', () => {
    const { container } = render(
      <FspSection
        businessArea='afghanistan'
        paymentPlan={{ ...fakeApolloPaymentPlan, deliveryMechanisms: [] }}
      />
    );
    expect(container).toMatchSnapshot();
  });

  it('should render Edit FSP', () => {
    const { container } = render(<FspSection businessArea='afghanistan' paymentPlan={fakeApolloPaymentPlan} />);
    expect(container).toMatchSnapshot();
  });
});
