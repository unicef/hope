import React from 'react';
import { MockedProvider } from '@apollo/react-testing';
import { render } from '../../../testUtils/testUtils';
import { fakeHousehold } from '../../../../fixtures/population/fakeHousehold';
import { fakeHouseholdChoices } from '../../../../fixtures/population/fakeHouseholdChoices';
import { fakeApolloAllGrievances } from '../../../../fixtures/grievances/fakeApolloAllGrievances';
import { fakeGrievancesChoices } from '../../../../fixtures/grievances/fakeGrievancesChoices';
import { HouseholdDetails } from './HouseholdDetails';

describe('components/population/HouseholdDetails', () => {
  it('should render', () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllGrievances}
      >
        <HouseholdDetails
          businessArea='afghanistan'
          household={fakeHousehold}
          choicesData={fakeHouseholdChoices}
          grievancesChoices={fakeGrievancesChoices}
        />
      </MockedProvider>
    );
    expect(container).toMatchSnapshot();
  });
});