import React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { GreyInfoCard } from './GreyInfoCard';

describe('components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/GreyInfoCard', () => {
  it('should render', () => {
    const { container } = render(
      <GreyInfoCard
        topMessage='Test top message'
        topDate='2022-01-01'
        approvals={
          fakeApolloPaymentPlan.approvalProcess.edges[0].node.actions.approval
        }
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
