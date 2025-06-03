import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { fakeBaseUrl } from '../../../../../fixtures/core/fakeBaseUrl';
import PaymentPlanDetails from './PaymentPlanDetails';

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
