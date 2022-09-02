import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from 'react-dom/test-utils';
import wait from 'waait';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/payments/fakeApolloPaymentPlan';
import { fakeActionPpMutation } from '../../../../../fixtures/payments/fakeApolloActionPaymentPlanMutation';
import { render } from '../../../../testUtils/testUtils';
import { RejectPaymentPlan } from './RejectPaymentPlan';

describe(
  'components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/RejectPaymentPlan',
  () => {
    it('should render', async () => {
      const { container } = render(
        <MockedProvider
          addTypename={false}
          mocks={fakeActionPpMutation}
        >
          <RejectPaymentPlan paymentPlanId={fakeApolloPaymentPlan.id} />
        </MockedProvider>
        ,
      );

      await act(() => wait(0)); // wait for the mutation to complete

      expect(container).toMatchSnapshot();
    });
  });
