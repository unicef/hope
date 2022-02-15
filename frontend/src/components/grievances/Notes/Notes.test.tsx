import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { Notes } from './Notes';
import { fakeGrievanceTicket } from '../../../../fixtures/grievances/fakeGrievanceTicket';

describe('components/grievances/Notes', () => {
  it('should render', () => {
    const { container } = render(
      <Notes notes={fakeGrievanceTicket.ticketNotes} canAddNote={true} />,
    );
    expect(container).toMatchSnapshot();
  });
});
