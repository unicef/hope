import React from 'react';
import { render } from '../../../../../testUtils/testUtils';
import { fakeChartTicketsByStatus } from '../../../../../../fixtures/grievances/grievancesDashboard/fakeChartTicketsByStatus';
import { TicketsByStatusSection } from './TicketsByStatusSection';

describe('components/grievances/GrievancesDashboard/TicketsByStatusSection', () => {
  it('should render', () => {
    const { container } = render(
      <TicketsByStatusSection data={fakeChartTicketsByStatus} />,
    );
    expect(container).toMatchSnapshot();
  });
});
