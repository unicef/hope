import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { fakeGrievanceTicket } from '../../../../fixtures/grievances/fakeGrievanceTicket';
import { fakeGrievancesChoices } from '../../../../fixtures/grievances/fakeGrievancesChoices';
import { fakeBaseUrl } from '../../../../fixtures/core/fakeBaseUrl';
import { GrievancesDetails } from './GrievancesDetails';

describe('components/grievances/GrievancesDetails', () => {
  it('should render', () => {
    const { container } = render(
      <GrievancesDetails
        baseUrl={fakeBaseUrl}
        ticket={fakeGrievanceTicket}
        choicesData={fakeGrievancesChoices}
        canViewHouseholdDetails
        canViewIndividualDetails
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
