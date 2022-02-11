import React from 'react';
import { render } from '../../../testUtils/testUtils';
import { fakeHouseholdChoices } from '../../../../fixtures/population/fakeHouseholdChoices';
import { fakeIndividual } from '../../../../fixtures/population/fakeIndividual';
import { IndividualBioData } from './IndividualBioData';

describe('components/population/IndividualBioData', () => {
  it('should render', () => {
    const { container } = render(
      <IndividualBioData
        businessArea='afghanistan'
        individual={fakeIndividual}
        choicesData={fakeHouseholdChoices}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
