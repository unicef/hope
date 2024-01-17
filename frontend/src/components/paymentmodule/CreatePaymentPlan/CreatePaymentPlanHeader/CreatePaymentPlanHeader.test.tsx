import React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { CreatePaymentPlanHeader } from './CreatePaymentPlanHeader';
import { fakeBaseUrl } from '../../../../../fixtures/core/fakeBaseUrl';

describe('components/paymentmodule/CreatePaymentPlanHeader', () => {
  it('should render', () => {
    const { container } = render(
      <CreatePaymentPlanHeader
        handleSubmit={() => Promise.resolve()}
        baseUrl={fakeBaseUrl}
        permissions={[PERMISSIONS.PM_VIEW_LIST]}
        loadingCreate={false}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
