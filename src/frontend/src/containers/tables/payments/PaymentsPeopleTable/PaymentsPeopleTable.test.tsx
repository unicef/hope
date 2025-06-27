import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import wait from 'waait';
import { fakeHousehold } from '../../../../../fixtures/population/fakeHousehold';
import { render } from '../../../../testUtils/testUtils';
import { fakeApolloAllPaymentsHousehold } from '../../../../../fixtures/payments/fakeApolloAllPaymentsHousehold';
import PaymentsPeopleTable from './PaymentsPeopleTable';

describe('containers/tables/payments/PaymentsPeopleTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentsHousehold}
      >
        <PaymentsPeopleTable
          household={fakeHousehold}
          openInNewTab={false}
          businessArea="afghanistan"
          canViewPaymentRecordDetails
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
        mocks={fakeApolloAllPaymentsHousehold}
      >
        <PaymentsPeopleTable
          household={fakeHousehold}
          openInNewTab={false}
          businessArea="afghanistan"
          canViewPaymentRecordDetails
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
