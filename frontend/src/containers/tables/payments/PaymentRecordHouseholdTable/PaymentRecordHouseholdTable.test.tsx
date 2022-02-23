import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { PaymentRecordHouseholdTable } from '.';
import { fakeApolloAllPaymentRecords } from '../../../../../fixtures/payments/fakeApolloAllPaymentRecords';
import { fakeHousehold } from '../../../../../fixtures/population/fakeHousehold';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';

describe('containers/tables/payments/PaymentRecordHouseholdTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllPaymentRecords}>
        <PaymentRecordHouseholdTable
          household={fakeHousehold}
          openInNewTab={false}
          businessArea='afghanistan'
          canViewPaymentRecordDetails={true}
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
        mocks={fakeApolloAllPaymentRecords}
      >
        <PaymentRecordHouseholdTable
          household={fakeHousehold}
          openInNewTab={false}
          businessArea='afghanistan'
          canViewPaymentRecordDetails={true}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
