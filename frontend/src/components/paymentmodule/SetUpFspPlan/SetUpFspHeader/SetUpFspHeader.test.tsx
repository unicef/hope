import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { SetUpFspHeader } from './SetUpFspHeader';

describe('components/paymentmodule/SetUpFspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <SetUpFspHeader
        handleSubmit={jest.fn()}
        businessArea='afghanistan'
        permissions={[PERMISSIONS.PAYMENT_MODULE_VIEW_LIST]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
