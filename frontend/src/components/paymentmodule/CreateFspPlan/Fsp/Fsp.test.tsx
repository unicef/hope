import React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { Fsp } from './Fsp';

describe('components/paymentmodule/Fsp', () => {
  it('should render', () => {
    const { container } = render(<Fsp index={0} baseName='wallet' />);
    expect(container).toMatchSnapshot();
  });
});
