import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from 'react-dom/test-utils';
import wait from 'waait';
import { fakeApolloPaymentPlan } from '../../../../../../fixtures/payments/fakeApolloPaymentPlan';
import { fakeActionPpMutation } from '../../../../../../fixtures/payments/fakeApolloActionPaymentPlanMutation';
import { render } from '../../../../../testUtils/testUtils';
import { InAuthorizationPaymentPlanHeaderButtons } from './InAuthorizationPaymentPlanHeaderButtons';

describe(
  'components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InAuthorizationPaymentPlanHeaderButtons',
  () => {
    it('should render with buttons', async () => {
      const { container } = render(
        <MockedProvider
          addTypename={false}
          mocks={fakeActionPpMutation}
        >
        <InAuthorizationPaymentPlanHeaderButtons
          paymentPlan={fakeApolloPaymentPlan}
          canReject
          canAuthorize
        />
        </MockedProvider>
        ,
      );

      await act(() => wait(0)); // wait for the mutation to complete

      expect(container).toMatchSnapshot();
    });
  });
