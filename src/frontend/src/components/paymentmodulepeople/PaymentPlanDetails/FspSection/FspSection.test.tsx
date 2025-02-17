import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { FspSection } from './FspSection';

describe('components/paymentmodule/PaymentPlanDetails/FspSection', () => {
  it('should render not setup FSP', () => {
    const { container } = render(
      <FspSection
        paymentPlan={{ ...fakeApolloPaymentPlan, deliveryMechanism: null }}
      />,
    );
    expect(container).toMatchSnapshot();
  });

  it('should render FSP', () => {
    const { container } = render(
      <FspSection paymentPlan={fakeApolloPaymentPlan} />,
    );
    expect(container).toMatchSnapshot();
  });
});
