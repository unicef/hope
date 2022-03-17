import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { GrievancesDetails } from './GrievancesDetails';
import { fakeGrievanceTicket } from '../../../../fixtures/grievances/fakeGrievanceTicket';
import { fakeGrievancesChoices } from '../../../../fixtures/grievances/fakeGrievancesChoices';

describe('components/grievances/GrievancesDetails', () => {
  it('should render', () => {
    const { container } = render(
      <GrievancesDetails
        businessArea='afghanistan'
        ticket={fakeGrievanceTicket}
        choicesData={fakeGrievancesChoices}
        canViewHouseholdDetails={true}
        canViewIndividualDetails={true}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
