import * as React from 'react';
import { PERMISSIONS } from '../../../../config/permissions';
import { render } from '../../../../testUtils/testUtils';
import { CreatePaymentPlanHeader } from './CreatePaymentPlanHeader';

describe('components/paymentmodule/CreatePaymentPlanHeader', () => {
  it('should render', () => {
    const { container } = render(
      <CreatePaymentPlanHeader
        handleSubmit={() => Promise.resolve()}
        permissions={[PERMISSIONS.PM_VIEW_LIST]}
        loadingCreate={false}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
