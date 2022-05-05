import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { Fsp } from './Fsp';

describe('components/paymentmodule/Fsp', () => {
  it('should render', () => {
    const { container } = render(
      <Fsp permissions={[PERMISSIONS.PAYMENT_MODULE_VIEW_LIST]} />,
    );
    expect(container).toMatchSnapshot();
  });
});
