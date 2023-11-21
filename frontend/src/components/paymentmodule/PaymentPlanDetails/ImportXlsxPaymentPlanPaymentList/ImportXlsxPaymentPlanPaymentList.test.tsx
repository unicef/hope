import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { fakeImportXlsxPpListMutation } from '../../../../../fixtures/paymentmodule/fakeImportXlsxPpListMutation';
import { render } from '../../../../testUtils/testUtils';
import { ImportXlsxPaymentPlanPaymentList } from './ImportXlsxPaymentPlanPaymentList';
import { PERMISSIONS } from '../../../../config/permissions';

describe('components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentList', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeImportXlsxPpListMutation}>
        <ImportXlsxPaymentPlanPaymentList
          permissions={[PERMISSIONS.PM_IMPORT_XLSX_WITH_ENTITLEMENTS]}
          paymentPlan={fakeApolloPaymentPlan}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
