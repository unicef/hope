import React from 'react';
import { render } from '../../../../../testUtils/testUtils';
import { fakeChartTicketsByLocationAndCategory } from '../../../../../../fixtures/grievances/grievancesDashboard/fakeChartTicketsByLocationAndCategory';
import { TicketsByLocationAndCategorySection } from './TicketsByLocationAndCategorySection';

describe('components/grievances/GrievancesDashboard/TicketsByLocationAndCategorySection', () => {
  it('should render', () => {
    const { container } = render(
      <TicketsByLocationAndCategorySection
        data={fakeChartTicketsByLocationAndCategory}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
