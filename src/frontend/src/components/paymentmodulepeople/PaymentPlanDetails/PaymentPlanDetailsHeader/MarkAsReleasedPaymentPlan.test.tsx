import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import wait from 'waait';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { fakeActionPpMutation } from '../../../../../fixtures/paymentmodule/fakeApolloActionPaymentPlanMutation';
import { render } from '../../../../testUtils/testUtils';
import { MarkAsReleasedPaymentPlan } from './MarkAsReleasedPaymentPlan';

describe('components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/MarkAsReleasedPaymentPlan', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeActionPpMutation}>
        <MarkAsReleasedPaymentPlan paymentPlan={fakeApolloPaymentPlan} />
      </MockedProvider>,
    );

    await act(() => wait(0)); // wait for the mutation to complete

    expect(container).toMatchSnapshot();
  });
});
