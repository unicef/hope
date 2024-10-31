import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import wait from 'waait';
import { fakeApolloAllPaymentsForTable } from '../../../../../fixtures/payments/fakeApolloAllPaymentsForTable';
import { fakeApolloAllPaymentPlansForTable } from '../../../../../fixtures/payments/fakeApolloAllPaymentPlansForTable';
import { render } from '../../../../testUtils/testUtils';
import { PaymentPlanQuery } from '@generated/graphql';
import { PeoplePaymentsTable } from './PeoplePaymentsTable';
import { PERMISSIONS } from '../../../../config/permissions';

const paymentPlan = fakeApolloAllPaymentPlansForTable[0].result.data
  .allPaymentPlans.edges[0].node as PaymentPlanQuery['paymentPlan'];

describe('containers/tables/paymentmodule/PeoplePaymentsTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllPaymentsForTable}>
        <PeoplePaymentsTable
          canViewDetails={false}
          businessArea="afghanistan"
          paymentPlan={paymentPlan}
          permissions={[
            PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION,
            PERMISSIONS.PM_VIEW_FSP_AUTH_CODE,
          ]}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllPaymentsForTable}>
        <PeoplePaymentsTable
          canViewDetails={false}
          businessArea="afghanistan"
          paymentPlan={paymentPlan}
          permissions={[
            PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION,
            PERMISSIONS.PM_VIEW_FSP_AUTH_CODE,
          ]}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });
});
