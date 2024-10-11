import * as React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { AcceptanceProcessRow } from './AcceptanceProcessRow';

describe('components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcessRow', () => {
  it('should render', () => {
    const { container } = render(
      <AcceptanceProcessRow
        paymentPlan={fakeApolloPaymentPlan}
        acceptanceProcess={fakeApolloPaymentPlan.approvalProcess.edges[0].node}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
