import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { CreateSetUpFspHeader } from './CreateSetUpFspHeader';

describe('components/paymentmodule/CreateSetUpFspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <CreateSetUpFspHeader
        handleSubmit={jest.fn()}
        businessArea='afghanistan'
        permissions={[PERMISSIONS.PAYMENT_MODULE_VIEW_LIST]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
