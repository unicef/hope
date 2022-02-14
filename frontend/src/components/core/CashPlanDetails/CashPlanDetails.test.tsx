import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { fakeCashPlan } from '../../../../fixtures/payments/fakeCashPlan';
import { CashPlanDetails } from '.';

describe('components/core/CashPlanDetails', () => {
  it('should render', () => {
    const { container } = render(
      <CashPlanDetails
        businessArea='afghanistan'
        cashPlan={fakeCashPlan}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
