import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react-dom/test-utils';
import wait from 'waait';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { fakeActionPpMutation } from '../../../../../fixtures/paymentmodule/fakeApolloActionPaymentPlanMutation';
import { render } from '../../../../testUtils/testUtils';
import { PeoplePaymentPlanDetailsResults } from './PeoplePaymentPlanDetailsResults';

describe('components/paymentmodule/PaymentPlanDetails/PeoplePaymentPlanDetailsHeader/PaymentPlanDetailsResults', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeActionPpMutation}>
        <PeoplePaymentPlanDetailsResults paymentPlan={fakeApolloPaymentPlan} />
      </MockedProvider>,
    );

    await act(() => wait(0)); // wait for the mutation to complete

    expect(container).toMatchSnapshot();
  });
});
