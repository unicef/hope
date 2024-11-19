import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import wait from 'waait';
import { fakeApolloAllPaymentRecordsHousehold } from '../../../../../fixtures/payments/fakeApolloAllPaymentRecordsHousehold';
import { fakeHousehold } from '../../../../../fixtures/population/fakeHousehold';
import { render } from '../../../../testUtils/testUtils';
import { PaymentRecordAndPaymentPeopleTable } from '.';

describe('containers/tables/payments/PaymentRecordAndPaymentPeopleTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllPaymentRecordsHousehold}
      >
        <PaymentRecordAndPaymentPeopleTable
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
        mocks={fakeApolloAllPaymentRecordsHousehold}
      >
        <PaymentRecordAndPaymentPeopleTable
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
