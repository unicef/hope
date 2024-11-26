import { fakeIndividual } from '../../../../../../fixtures/population/fakeIndividual';
import { fakeHouseholdChoices } from '../../../../../../fixtures/population/fakeHouseholdChoices';
import { render } from '../../../../../testUtils/testUtils';
import { RegistrationIndividualBioData } from './RegistrationIndividualBioData';

describe('components/rdi/details/individual/RegistrationIndividualBioData', () => {
  it('should render', () => {
    const { container } = render(
      <RegistrationIndividualBioData
        individual={fakeIndividual}
        choicesData={fakeHouseholdChoices}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
