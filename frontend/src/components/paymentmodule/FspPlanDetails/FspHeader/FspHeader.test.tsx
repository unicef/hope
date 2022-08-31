import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { FspHeader } from './FspHeader';

describe('components/paymentmodule/FspPlanDetails/FspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <FspHeader
        businessArea='afghanistan'
        permissions={[PERMISSIONS.PAYMENT_MODULE_VIEW_LIST]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
