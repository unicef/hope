import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { CreateSetUpFspHeader } from './CreateSetUpFspHeader';
import { fakeBaseUrl } from '../../../../../fixtures/core/fakeBaseUrl';

describe('components/paymentmodule/CreateSetUpFsp/CreateSetUpFspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <CreateSetUpFspHeader
        baseUrl={fakeBaseUrl}
        permissions={[PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
