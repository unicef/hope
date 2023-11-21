import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { EditFspHeader } from './EditFspHeader';
import { fakeBaseUrl } from '../../../../../fixtures/core/fakeBaseUrl';

describe('components/paymentmodule/EditFspHeader', () => {
  it('should render', () => {
    const { container } = render(
      <EditFspHeader
        handleSubmit={jest.fn()}
        baseUrl={fakeBaseUrl}
        permissions={[PERMISSIONS.PM_VIEW_LIST]}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
