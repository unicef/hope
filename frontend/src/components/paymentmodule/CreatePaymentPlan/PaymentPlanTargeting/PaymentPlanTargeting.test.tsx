import React from 'react';
import { fakeAllTargetPopulation } from '../../../../../fixtures/targeting/fakeAllTargetPopulation';
import { render } from '../../../../testUtils/testUtils';
import { PaymentPlanTargeting } from './PaymentPlanTargeting';

describe('components/paymentmodule/PaymentPlanTargeting', () => {
  it('should render', () => {
    const { container } = render(
      <PaymentPlanTargeting
        allTargetPopulations={fakeAllTargetPopulation}
        loading={false}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
