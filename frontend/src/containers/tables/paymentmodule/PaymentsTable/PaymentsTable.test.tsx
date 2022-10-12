import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { fakeApolloAllPaymentsForTable } from '../../../../../fixtures/payments/fakeApolloAllPaymentsForTable';
import { fakeApolloAllPaymentPlansForTable } from '../../../../../fixtures/payments/fakeApolloAllPaymentPlansForTable';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { PaymentsTable } from './PaymentsTable';

const paymentPlan = fakeApolloAllPaymentPlansForTable[0].result.data.allPaymentPlans.edges[0].node as PaymentPlanQuery['paymentPlan'];

describe('containers/tables/paymentmodule/PaymentsTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentsForTable}
      >
        <PaymentsTable
          canViewDetails={false}
          businessArea='afghanistan'
          paymentPlan={paymentPlan}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', async () => {
    const { container } = render(
      <MockedProvider
        link={new ApolloLoadingLink()}
        addTypename={false}
        mocks={fakeApolloAllPaymentsForTable}
      >
        <PaymentsTable
          canViewDetails={false}
          businessArea='afghanistan'
          paymentPlan={paymentPlan}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });
});
