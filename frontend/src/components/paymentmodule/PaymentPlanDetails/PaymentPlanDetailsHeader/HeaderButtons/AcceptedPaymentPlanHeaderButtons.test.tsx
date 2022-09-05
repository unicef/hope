import React from 'react';
// import { fakeApolloPaymentPlan } from '../../../../../../fixtures/payments/fakeApolloPaymentPlan';
import { render } from '../../../../../testUtils/testUtils';
import { AcceptedPaymentPlanHeaderButtons } from './AcceptedPaymentPlanHeaderButtons';

describe(
  'components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/AcceptedPaymentPlanHeaderButtons',
  () => {
    it('should render with no buttons', () => {
      const { container } = render(
        <AcceptedPaymentPlanHeaderButtons
          canDownloadXlsx={false}
          canSendToFsp={false}
        />,
      );

      const buttons = container.querySelectorAll('button');
      expect(buttons).toHaveLength(0);

      expect(container).toMatchSnapshot();
    });

    it('should render with buttons', () => {
      const { container } = render(
        <AcceptedPaymentPlanHeaderButtons
          canDownloadXlsx
          canSendToFsp
        />,
      );

      const buttons = container.querySelectorAll('button');
      expect(buttons).toHaveLength(2);

      expect(container).toMatchSnapshot();
    });
  });
