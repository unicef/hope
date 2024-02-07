import * as React from 'react';
import { fakeHouseholdChoices } from '../../../../../../fixtures/population/fakeHouseholdChoices';
import { fakeImportedIndividualDetailedFragment } from '../../../../../../fixtures/registration/fakeImportedIndividualDetailedFragment';
import { render } from '../../../../../testUtils/testUtils';
import { RegistrationIndividualBioData } from './RegistrationIndividualBioData';

describe('components/rdi/details/individual/RegistrationIndividualBioData', () => {
  it('should render', () => {
    const { container } = render(
      <RegistrationIndividualBioData
        businessArea="afghanistan"
        individual={fakeImportedIndividualDetailedFragment}
        choicesData={fakeHouseholdChoices}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
