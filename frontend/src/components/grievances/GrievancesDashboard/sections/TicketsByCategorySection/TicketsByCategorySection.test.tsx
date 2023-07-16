import React from 'react';
import { render } from '../../../../../testUtils/testUtils';
import { fakeChartTicketsByCategory } from '../../../../../../fixtures/grievances/grievancesDashboard/fakeChartTicketsByCategory';
import { TicketsByCategorySection } from './TicketsByCategorySection';

describe('components/grievances/GrievancesDashboard/TicketsByCategorySection', () => {
  it('should render', () => {
    const { container } = render(
      <TicketsByCategorySection data={fakeChartTicketsByCategory} />,
    );
    expect(container).toMatchSnapshot();
  });
});
