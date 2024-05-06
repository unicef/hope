import * as React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { TotalNumberOfChildrenReachedSection } from './TotalNumberOfChildrenReachedSection';
import { fakeSectionChildReached } from '../../../../../fixtures/dashboard/fakeSectionChildReached';

describe('components/dashboard/TotalNumberOfChildrenReachedSection', () => {
  it('should render', () => {
    const { container } = render(
      <TotalNumberOfChildrenReachedSection data={fakeSectionChildReached} />,
    );
    expect(container).toMatchSnapshot();
  });
});
