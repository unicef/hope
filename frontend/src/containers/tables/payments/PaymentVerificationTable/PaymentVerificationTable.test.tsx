import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { fakeApolloAllCashPlansAndPaymentPlans } from '../../../../../fixtures/payments/fakeApolloAllCashPlansAndPaymentPlans';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { PaymentVerificationTable } from '.';

describe('containers/tables/payments/PaymentVerificationTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllCashPlansAndPaymentPlans}
      >
        <PaymentVerificationTable
          canViewDetails={false}
          businessArea='afghanistan'
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider
        link={new ApolloLoadingLink()}
        addTypename={false}
        mocks={fakeApolloAllCashPlansAndPaymentPlans}
      >
        <PaymentVerificationTable
          canViewDetails={false}
          businessArea='afghanistan'
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
