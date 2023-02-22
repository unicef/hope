import React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { EditPaymentPlanHeader } from './EditPaymentPlanHeader';

describe('components/paymentmodule/EditPaymentPlanHeader', () => {
  it('should render', () => {
    const { container } = render(
      <EditPaymentPlanHeader
        handleSubmit={jest.fn()}
        businessArea='afghanistan'
        permissions={[PERMISSIONS.PM_VIEW_LIST]}
        paymentPlan={fakeApolloPaymentPlan}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
