import React from 'react';
import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react-dom/test-utils';
import wait from 'waait';
import { fakeApolloAllSteficonRules } from '../../../../../fixtures/steficon/fakeApolloAllSteficonRules';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/payments/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { Entitlement } from './Entitlement';

describe('components/paymentmodule/PaymentPlanDetails/Entitlement', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllSteficonRules}
      >
        <Entitlement paymentPlan={fakeApolloPaymentPlan} />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
});
