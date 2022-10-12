import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { EditSetUpFspHeader } from './EditSetUpFspHeader';

describe('components/paymentmodule/EditSetUpFsp/EditSetUpFspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <EditSetUpFspHeader
        businessArea='afghanistan'
        permissions={[PERMISSIONS.PAYMENT_MODULE_VIEW_LIST]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
