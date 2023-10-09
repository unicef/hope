import React from 'react';
import { render } from '../../testUtils/testUtils';
import { fakeApolloMe } from '../../../fixtures/core/fakeApolloMe';
import { MessageDialog } from './MessageDialog';

describe('components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/MessageDialog', () => {
  it('should render', () => {
    const { container } = render(
      <MessageDialog
        comment='Test top message'
        date='2022-01-01'
        author={fakeApolloMe[0].result.data.me}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
