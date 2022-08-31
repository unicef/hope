import React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { PaymentPlanParameters } from './PaymentPlanParameters';

describe('components/paymentmodule/PaymentPlanParameters', () => {
  it('should render', () => {
    const values = {
      targetPopulation: '',
      startDate: null,
      endDate: null,
      currency: null,
    };
    const { container } = render(<PaymentPlanParameters values={values} currencyChoicesData={[]} />);
    expect(container).toMatchSnapshot();
  });
});
