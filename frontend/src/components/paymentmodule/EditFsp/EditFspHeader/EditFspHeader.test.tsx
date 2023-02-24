import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { EditFspHeader } from './EditFspHeader';

describe('components/paymentmodule/EditFspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <EditFspHeader
        handleSubmit={jest.fn()}
        businessArea='afghanistan'
        permissions={[PERMISSIONS.PM_VIEW_LIST]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
