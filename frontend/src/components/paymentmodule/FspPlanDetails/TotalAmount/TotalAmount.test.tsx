import React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { TotalAmount } from './TotalAmount';

describe('components/paymentmodule/FspPlanDetails/TotalAmount', () => {
  it('should render', () => {
    const { container } = render(<TotalAmount />);
    expect(container).toMatchSnapshot();
  });
});
