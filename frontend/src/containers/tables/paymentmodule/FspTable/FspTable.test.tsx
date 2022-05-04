import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { FspTable } from './FspTable';
import { fakeApolloAllCashPlansPaymentVerification } from '../../../../../fixtures/payments/fakeApolloAllCashPlansPaymentVerification';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';

describe('containers/tables/payments/FspTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllCashPlansPaymentVerification}
      >
        <FspTable
          canViewDetails={false}
          filter={{}}
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
        mocks={fakeApolloAllCashPlansPaymentVerification}
      >
        <FspTable
          canViewDetails={false}
          filter={{}}
          businessArea='afghanistan'
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
