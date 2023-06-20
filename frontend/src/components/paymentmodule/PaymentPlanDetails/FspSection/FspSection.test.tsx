import React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { FspSection } from './FspSection';
import { fakeBaseUrl } from '../../../../../fixtures/core/fakeBaseUrl';

describe('components/paymentmodule/PaymentPlanDetails/FspSection', () => {
  it('should render Set Up FSP', () => {
    const { container } = render(
      <FspSection
        baseUrl={fakeBaseUrl}
        paymentPlan={{ ...fakeApolloPaymentPlan, deliveryMechanisms: [] }}
      />,
    );
    expect(container).toMatchSnapshot();
  });

  it('should render Edit FSP', () => {
    const { container } = render(
      <FspSection baseUrl={fakeBaseUrl} paymentPlan={fakeApolloPaymentPlan} />,
    );
    expect(container).toMatchSnapshot();
  });
});
