import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';

import * as React from 'react';
import wait from 'waait';
import { PaymentRecordTable } from '.';
import { fakeApolloAllPaymentRecords } from '../../../../../fixtures/payments/fakeApolloAllPaymentRecords';
import { fakeCashPlan } from '../../../../../fixtures/payments/fakeCashPlan';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';

describe('containers/tables/payments/PaymentRecordTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllPaymentRecords}>
        <PaymentRecordTable cashPlan={fakeCashPlan} openInNewTab={false} />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllPaymentRecords}>
        <PaymentRecordTable cashPlan={fakeCashPlan} openInNewTab={false} />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
