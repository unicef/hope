import * as React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../../testUtils/testUtils';
import { VolumeByDeliveryMechanismSection } from './VolumeByDeliveryMechanismSection';

describe('components/paymentmodule/PaymentPlanDetails/VolumeByDeliveryMechanismSection', () => {
  it('should render', () => {
    const { container } = render(
      <VolumeByDeliveryMechanismSection paymentPlan={fakeApolloPaymentPlan} />,
    );
    expect(container).toMatchSnapshot();
  });
});
