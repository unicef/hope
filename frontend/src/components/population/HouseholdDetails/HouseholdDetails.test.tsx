import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { HouseholdDetails } from './HouseholdDetails';
import { fakeHousehold } from '../../../../fixtures/population/fakeHousehold';
import { fakeHouseholdChoices } from '../../../../fixtures/population/fakeHouseholdChoices';

describe('components/HouseholdDetails', () => {
  it('should render', () => {
    const { container } = render(
      <HouseholdDetails
        businessArea='afghanistan'
        household={fakeHousehold}
        choicesData={fakeHouseholdChoices}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
