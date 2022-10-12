import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { CreateSetUpFspHeader } from './CreateSetUpFspHeader';

describe('components/paymentmodule/CreateSetUpFsp/CreateSetUpFspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <CreateSetUpFspHeader
        businessArea='afghanistan'
        permissions={[PERMISSIONS.FINANCIAL_SERVICE_PROVIDER_CREATE]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
