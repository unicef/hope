import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import wait from 'waait';
import { fakeApolloPaymentPlan } from '../../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { fakeActionPpMutation } from '../../../../../../fixtures/paymentmodule/fakeApolloActionPaymentPlanMutation';
import { render } from '../../../../../testUtils/testUtils';
import { PERMISSIONS } from '../../../../../config/permissions';
import { LockedPaymentPlanHeaderButtons } from './LockedPaymentPlanHeaderButtons';

describe('components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedPaymentPlanHeaderButtons', () => {
  it('should render with buttons', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeActionPpMutation}>
        <LockedPaymentPlanHeaderButtons
          paymentPlan={fakeApolloPaymentPlan}
          canUnlock={false}
          permissions={[PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]}
        />
      </MockedProvider>,
    );

    await act(() => wait(0)); // wait for the mutation to complete

    expect(container).toMatchSnapshot();
  });
});
