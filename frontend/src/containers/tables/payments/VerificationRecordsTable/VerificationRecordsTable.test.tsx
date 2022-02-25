import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { VerificationRecordsTable } from '.';
import { fakeApolloAllPaymentVerifications } from '../../../../../fixtures/payments/fakeApolloAllPaymentVerifications';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';

describe('containers/tables/payments/VerificationRecordsTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentVerifications}
      >
        <VerificationRecordsTable
          cashPlanId='Q2FzaFBsYW5Ob2RlOmNiNzBjYjdmLWY0N2EtNDI5Yy04Y2FjLTk0YzU0MDRiOTFkZA=='
          filter={{}}
          canViewRecordDetails={true}
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
          cashPlanId='Q2FzaFBsYW5Ob2RlOmNiNzBjYjdmLWY0N2EtNDI5Yy04Y2FjLTk0YzU0MDRiOTFkZA=='
          filter={{}}
          canViewRecordDetails={true}
          businessArea='afghanistan'
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
