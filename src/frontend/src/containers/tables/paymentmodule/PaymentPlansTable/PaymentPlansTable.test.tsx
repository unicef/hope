import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import wait from 'waait';
import { fakeApolloAllPaymentPlansForTable } from '../../../../../fixtures/payments/fakeApolloAllPaymentPlansForTable';
import { render } from '../../../../testUtils/testUtils';
import { PaymentPlansTable } from './PaymentPlansTable';

describe('containers/tables/payments/PaymentPlansTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentPlansForTable}
      >
        <PaymentPlansTable
          canViewDetails={false}
          filter={{
            search: '',
            dispersionStartDate: undefined,
            dispersionEndDate: undefined,
            status: [],
            totalEntitledQuantityFrom: null,
            totalEntitledQuantityTo: null,
            isFollowUp: null,
          }}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  }, 10000); // Increase the timeout to 10 seconds

  it('should render loading', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentPlansForTable}
      >
        <PaymentPlansTable
          canViewDetails={false}
          filter={{
            search: '',
            dispersionStartDate: undefined,
            dispersionEndDate: undefined,
            status: [],
            totalEntitledQuantityFrom: null,
            totalEntitledQuantityTo: null,
            isFollowUp: null,
          }}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  }, 10000); // Increase the timeout to 10 seconds
});
