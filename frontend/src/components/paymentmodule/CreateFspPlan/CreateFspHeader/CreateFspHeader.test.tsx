import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { CreateFspHeader } from './CreateFspHeader';

describe('components/paymentmodule/CreateFspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <CreateFspHeader
        handleSubmit={jest.fn()}
        businessArea='afghanistan'
        permissions={[PERMISSIONS.PAYMENT_MODULE_VIEW_LIST]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
