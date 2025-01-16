import { MockedProvider } from '@apollo/react-testing';
import wait from 'waait';
import { act } from 'react';
import { fakeApolloPaymentPlan } from '../../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { fakeExportXlsxPpListPerFspMutation } from '../../../../../../fixtures/paymentmodule/fakeExportXlsxPpListPerFspMutation';
import { render } from '../../../../../testUtils/testUtils';
import { AcceptedPaymentPlanHeaderButtons } from './AcceptedPaymentPlanHeaderButtons';

describe('components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/AcceptedPaymentPlanHeaderButtons', () => {
  it('should render disabled buttons', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeExportXlsxPpListPerFspMutation}
      >
        <AcceptedPaymentPlanHeaderButtons
          canSendToPaymentGateway={false}
          canSplit={false}
          paymentPlan={fakeApolloPaymentPlan}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });
});
