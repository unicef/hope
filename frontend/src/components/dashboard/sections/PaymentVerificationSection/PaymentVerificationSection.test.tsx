import * as React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { PaymentVerificationSection } from './PaymentVerificationSection';
import { fakeChartPaymentVerification } from '../../../../../fixtures/dashboard/fakeChartPaymentVerification';

describe('components/dashboard/PaymentVerificationSection', () => {
  it('should render', () => {
    const { container } = render(
      <PaymentVerificationSection data={fakeChartPaymentVerification} />,
    );
    expect(container).toMatchSnapshot();
  });
});
