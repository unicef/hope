import * as React from 'react';
import { fakeHousehold } from '../../../../../fixtures/population/fakeHousehold';
import { fakeHouseholdChoices } from '../../../../../fixtures/population/fakeHouseholdChoices';
import { render } from '../../../../testUtils/testUtils';
import { HouseholdIndividualsTable } from './HouseholdIndividualsTable';

describe('components/tables/population/HouseholdIndividualsTable', () => {
  it('should render', () => {
    const { container } = render(
      <HouseholdIndividualsTable
        household={fakeHousehold}
        choicesData={fakeHouseholdChoices}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
