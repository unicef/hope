import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { fakeGrievanceTicket } from '../../../../fixtures/grievances/fakeGrievanceTicket';
import { fakeGrievancesChoices } from '../../../../fixtures/grievances/fakeGrievancesChoices';
import { GrievancesDetails } from './GrievancesDetails';

describe('components/grievances/GrievancesDetails', () => {
  it('should render', () => {
    const { container } = render(
      <GrievancesDetails
        businessArea='afghanistan'
        ticket={fakeGrievanceTicket}
        choicesData={fakeGrievancesChoices}
        canViewHouseholdDetails
        canViewIndividualDetails
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
