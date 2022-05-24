import React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { FspForm } from './FspForm';

describe('components/paymentmodule/FspForm', () => {
  it('should render', () => {
    const { container } = render(<FspForm index={0} baseName='wallet' />);
    expect(container).toMatchSnapshot();
  });
});
