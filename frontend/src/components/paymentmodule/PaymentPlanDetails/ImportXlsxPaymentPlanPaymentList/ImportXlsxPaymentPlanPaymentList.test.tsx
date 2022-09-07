import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { act } from 'react-dom/test-utils';
import wait from 'waait';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { fakeImportXlsxPpListMutation } from '../../../../../fixtures/paymentmodule/fakeImportXlsxPpListMutation';
import { render } from '../../../../testUtils/testUtils';
import { ImportXlsxPaymentPlanPaymentList } from './ImportXlsxPaymentPlanPaymentList';

describe('components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentList', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeImportXlsxPpListMutation}>
        <ImportXlsxPaymentPlanPaymentList paymentPlan={fakeApolloPaymentPlan} />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });
});
