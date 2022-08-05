import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { fakeApolloAllPaymentsForTable } from '../../../../../fixtures/payments/fakeApolloAllPaymentsForTable';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { PaymentsTable } from './PaymentsTable';

describe('containers/tables/payments/PaymentsTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentsForTable}
      >
        <PaymentsTable
          canViewDetails={false}
          filter={{paymentPlanId: ''}}
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
        mocks={fakeApolloAllPaymentsForTable}
      >
        <PaymentsTable
          canViewDetails={false}
          filter={{paymentPlanId:''}}
          businessArea='afghanistan'
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
