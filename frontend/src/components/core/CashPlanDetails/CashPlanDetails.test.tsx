import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { fakeCashPlan } from '../../../../fixtures/payments/fakeCashPlan';
import { CashPlanDetails } from '.';
import { fakeBaseUrl } from '../../../../fixtures/core/fakeBaseUrl';

describe('components/core/CashPlanDetails', () => {
  it('should render', () => {
    const { container } = render(
      <CashPlanDetails baseUrl={fakeBaseUrl} cashPlan={fakeCashPlan} />,
    );
    expect(container).toMatchSnapshot();
  });
});
