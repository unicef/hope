import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { fakeApolloAllPaymentVerifications } from '../../../../../fixtures/payments/fakeApolloAllPaymentVerifications';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { VerificationRecordsTable } from '.';

describe('containers/tables/payments/VerificationRecordsTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentVerifications}
      >
        <VerificationRecordsTable
          paymentPlanId='Q2FzaFBsYW5Ob2RlOjIyODExYzJjLWVmYTktNDRiYy1hYjM0LWQ0YjJkNjFmYThlNA=='
          // filter={{}}
          canViewRecordDetails
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
        mocks={fakeApolloAllPaymentVerifications}
      >
        <VerificationRecordsTable
          paymentPlanId='Q2FzaFBsYW5Ob2RlOjIyODExYzJjLWVmYTktNDRiYy1hYjM0LWQ0YjJkNjFmYThlNA=='
          // filter={{}}
          canViewRecordDetails
          businessArea='afghanistan'
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
