import { act } from 'react';
import { MockedProvider } from '@apollo/react-testing';
import wait from 'waait';
import { fakeApolloAllSteficonRules } from '../../../../../fixtures/steficon/fakeApolloAllSteficonRules';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { Entitlement } from './Entitlement';
import { PERMISSIONS } from '../../../../config/permissions';

describe('components/paymentmodule/PaymentPlanDetails/Entitlement', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllSteficonRules}>
        <Entitlement
          paymentPlan={fakeApolloPaymentPlan}
          permissions={[
            PERMISSIONS.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS,
          ]}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
});
