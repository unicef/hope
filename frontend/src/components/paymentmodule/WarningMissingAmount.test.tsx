import React from 'react';
import { render } from '../../testUtils/testUtils';
import { WarningMissingAmount } from './WarningMissingAmount';

describe('components/paymentmodule/WarningMissingAmount', () => {
  it('should render', () => {
    const { container } = render(
      <WarningMissingAmount amount={100000} currency='USD' />,
    );

    expect(container).toMatchSnapshot();
  });
});
