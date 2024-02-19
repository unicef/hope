import * as React from 'react';
import { fakeHouseholdChoices } from '../../../../../../fixtures/population/fakeHouseholdChoices';
import { fakeImportedHouseholdDetailedFragment } from '../../../../../../fixtures/registration/fakeImportedHouseholdDetailedFragment';
import { render } from '../../../../../testUtils/testUtils';
import { HouseholdDetails } from './HouseholdDetails';

describe('components/rdi/details/households/HouseholdDetails', () => {
  it('should render', () => {
    const { container } = render(
      <HouseholdDetails
        household={fakeImportedHouseholdDetailedFragment}
        choicesData={fakeHouseholdChoices}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
