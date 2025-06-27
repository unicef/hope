import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';

import wait from 'waait';
import { render } from '../../../../testUtils/testUtils';
import { fakeApolloAllPaymentPlansForTable } from '../../../../../fixtures/payments/fakeApolloAllPaymentPlansForTable';
import PaymentVerificationTable from './PaymentVerificationTable';

describe('containers/tables/payments/PaymentVerificationTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentPlansForTable}
      >
        <PaymentVerificationTable
          canViewDetails={false}
          businessArea="afghanistan"
          filter={{
            search: '',
            verificationStatus: [],
            serviceProvider: '',
            deliveryType: [],
            startDateGte: undefined,
            endDateLte: undefined,
          }}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentPlansForTable}
      >
        <PaymentVerificationTable
          canViewDetails={false}
          businessArea="afghanistan"
          filter={{
            search: '',
            verificationStatus: [],
            serviceProvider: '',
            deliveryType: [],
            startDateGte: undefined,
            endDateLte: undefined,
          }}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
