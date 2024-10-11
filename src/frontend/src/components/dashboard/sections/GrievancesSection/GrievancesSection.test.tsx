import * as React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { GrievancesSection } from './GrievancesSection';
import { fakeChartGrievances } from '../../../../../fixtures/dashboard/fakeChartGrievances';

describe('components/dashboard/GrievancesSection', () => {
  it('should render', () => {
    const { container } = render(
      <GrievancesSection data={fakeChartGrievances} />,
    );
    expect(container).toMatchSnapshot();
  });
});
