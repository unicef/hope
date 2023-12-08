import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { FspHeader } from './FspHeader';
import { fakeBaseUrl } from '../../../../../fixtures/core/fakeBaseUrl';

describe('components/paymentmodule/FspPlanDetails/FspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <FspHeader
        baseUrl={fakeBaseUrl}
        permissions={[PERMISSIONS.PM_VIEW_LIST]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
