import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { fakeGrievanceTicket } from '../../../../fixtures/grievances/fakeGrievanceTicket';
import { GrievancesSidebar } from '.';

describe('components/grievances/GrievancesSidebar', () => {
  it('should render', () => {
    const { container } = render(
      <GrievancesSidebar ticket={fakeGrievanceTicket} />,
    );
    expect(container).toMatchSnapshot();
  });
});
