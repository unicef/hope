import React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { DeliveryMechanismRow } from './DeliveryMechanismRow';

describe('components/paymentmodule/DeliveryMechanismRow', () => {
  it('should render', () => {
    const { container } = render(
      <DeliveryMechanismRow index={0} baseName='wallet' />,
    );
    expect(container).toMatchSnapshot();
  });
});
