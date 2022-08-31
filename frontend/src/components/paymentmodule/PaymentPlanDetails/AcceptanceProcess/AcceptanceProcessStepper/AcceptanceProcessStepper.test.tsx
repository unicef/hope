import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { fakeApolloPaymentPlan } from '../../../../../../fixtures/payments/fakeApolloPaymentPlan';
import { render } from '../../../../../testUtils/testUtils';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper';

describe('components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcessStepper', () => {
  it('should render default step Sent for Approval Date', async () => {
    const { container } = render(
      <AcceptanceProcessStepper
        acceptanceProcess={fakeApolloPaymentPlan.approvalProcess.edges[0].node}
        approvalNumberRequired={1}
        authorizationNumberRequired={1}
        financeReviewNumberRequired={1}
      />,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
  it('should render step Sent for Approval Date', async () => {
    const { container } = render(
      <AcceptanceProcessStepper
        acceptanceProcess={{...fakeApolloPaymentPlan.approvalProcess.edges[0].node, sentForApprovalDate: '2020-01-01'}}
        approvalNumberRequired={1}
        authorizationNumberRequired={1}
        financeReviewNumberRequired={1}
      />,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
  it('should render step Sent for Authorization Date', async () => {
    const { container } = render(
      <AcceptanceProcessStepper
        acceptanceProcess={{...fakeApolloPaymentPlan.approvalProcess.edges[0].node, sentForAuthorizationDate: '2020-01-01'}}
        approvalNumberRequired={1}
        authorizationNumberRequired={1}
        financeReviewNumberRequired={1}
      />,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
  it('should render step Sent for Finance Review Date', async () => {
    const { container } = render(
      <AcceptanceProcessStepper
        acceptanceProcess={{...fakeApolloPaymentPlan.approvalProcess.edges[0].node, sentForFinanceReviewDate: '2020-01-02'}}
        approvalNumberRequired={1}
        authorizationNumberRequired={1}
        financeReviewNumberRequired={1}
      />,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
});
