import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { DeliveryMechanismWarning } from './DeliveryMechanismWarning';

describe('components/paymentmodule/DeliveryMechanismWarning', () => {
  it('should render', () => {
    const { container } = render(
      <DeliveryMechanismWarning warning='Test DM warning comp' />,
    );
    expect(container).toMatchSnapshot();
  });
});
