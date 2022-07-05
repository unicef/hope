import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { CreatePaymentPlanHeader } from './CreatePaymentPlanHeader';

describe('components/paymentmodule/CreatePaymentPlanHeader', () => {
  it('should render', () => {
    const { container } = render(
      <CreatePaymentPlanHeader
        handleSubmit={jest.fn()}
        businessArea='afghanistan'
        permissions={[PERMISSIONS.PAYMENT_MODULE_VIEW_LIST]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
