import * as React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { TotalAmountTransferredSection } from './TotalAmountTransferredSection';
import { fakeSectionTotalTransferred } from '../../../../../fixtures/dashboard/fakeSectionTotalTransferred';

describe('components/dashboard/TotalAmountTransferredSection', () => {
  it('should render', () => {
    const { container } = render(
      <TotalAmountTransferredSection data={fakeSectionTotalTransferred} />,
    );
    expect(container).toMatchSnapshot();
  });
});
