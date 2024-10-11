import { act } from 'react';
import wait from 'waait';
import { fakeApolloPaymentPlan } from '../../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { render } from '../../../../../testUtils/testUtils';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper';

describe('components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcessStepper', () => {
  it('should render default step Sent for Approval Date', async () => {
    const { container } = render(
      <AcceptanceProcessStepper
        acceptanceProcess={fakeApolloPaymentPlan.approvalProcess.edges[0].node}
      />,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
  it('should render step Sent for Approval Date', async () => {
    const { container } = render(
      <AcceptanceProcessStepper
        acceptanceProcess={{
          ...fakeApolloPaymentPlan.approvalProcess.edges[0].node,
          sentForApprovalDate: '2020-01-01',
        }}
      />,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
  it('should render step Sent for Authorization Date', async () => {
    const { container } = render(
      <AcceptanceProcessStepper
        acceptanceProcess={{
          ...fakeApolloPaymentPlan.approvalProcess.edges[0].node,
          sentForAuthorizationDate: '2020-01-01',
        }}
      />,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
  it('should render step Sent for Finance Release Date', async () => {
    const { container } = render(
      <AcceptanceProcessStepper
        acceptanceProcess={{
          ...fakeApolloPaymentPlan.approvalProcess.edges[0].node,
          sentForFinanceReleaseDate: '2020-01-02',
        }}
      />,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
});
