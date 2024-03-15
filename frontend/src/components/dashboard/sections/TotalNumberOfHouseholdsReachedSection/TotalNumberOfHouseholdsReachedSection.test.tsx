import * as React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { TotalNumberOfHouseholdsReachedSection } from './TotalNumberOfHouseholdsReachedSection';
import { fakeSectionHouseholdsReached } from '../../../../../fixtures/dashboard/fakeSectionHouseholdsReached';

describe('components/dashboard/TotalNumberOfHouseholdsReachedSection', () => {
  it('should render', () => {
    const { container } = render(
      <TotalNumberOfHouseholdsReachedSection
        data={fakeSectionHouseholdsReached}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
