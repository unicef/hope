import * as React from 'react';
import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react-dom/test-utils';
import wait from 'waait';
import { fakeImportXlsxPpListPerFspMutation } from '../../../../../fixtures/paymentmodule/fakeImportXlsxPpListPerFspMutation';
import {
  fakeApolloPaymentPlan,
  fakeApolloPaymentPlanWithWrongBackgroundActionStatus,
} from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { PERMISSIONS } from '../../../../config/permissions';
import { ImportXlsxPaymentPlanPaymentListPerFsp } from './ImportXlsxPaymentPlanPaymentListPerFsp';

describe('components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentListPerFsp', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeImportXlsxPpListPerFspMutation}
      >
        <ImportXlsxPaymentPlanPaymentListPerFsp
          paymentPlan={fakeApolloPaymentPlan}
          permissions={[PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION]}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should not render', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeImportXlsxPpListPerFspMutation}
      >
        <ImportXlsxPaymentPlanPaymentListPerFsp
          paymentPlan={fakeApolloPaymentPlanWithWrongBackgroundActionStatus}
          permissions={[PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION]}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });
});
