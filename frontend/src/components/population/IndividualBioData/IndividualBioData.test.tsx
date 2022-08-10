import React from 'react';
import { MockedProvider } from '@apollo/react-testing';
import { render } from '../../../testUtils/testUtils';
import { fakeHouseholdChoices } from '../../../../fixtures/population/fakeHouseholdChoices';
import { fakeIndividual } from '../../../../fixtures/population/fakeIndividual';
import { fakeApolloAllGrievances } from '../../../../fixtures/grievances/fakeApolloAllGrievances';
import { fakeGrievancesChoices } from '../../../../fixtures/grievances/fakeGrievancesChoices';
import { IndividualBioData } from './IndividualBioData';

describe('components/population/IndividualBioData', () => {
  it('should render', () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllGrievances}
      >
        <IndividualBioData
          businessArea='afghanistan'
          individual={fakeIndividual}
          choicesData={fakeHouseholdChoices}
          grievancesChoices={fakeGrievancesChoices}
        />
      </MockedProvider>
    );
    expect(container).toMatchSnapshot();
  });
});
